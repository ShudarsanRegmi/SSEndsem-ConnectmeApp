import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, status
from typing import List, Optional
from app.database import get_db
from app.models import PostResponse, MessageResponse
from app.security import get_current_user, sanitize_input, log_audit_event
from app.media_security import validate_and_process_image
from app.config import settings

router = APIRouter(prefix="/api/v1/posts", tags=["Posts"])

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: Request,
    image: UploadFile = File(...),
    caption: Optional[str] = Form(""),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    client_ip = request.client.host if request.client else "unknown"

    # 1. Media validation & processing (Magic bytes, EXIF strip, UUID filename)
    image_url, file_sha256 = await validate_and_process_image(image)

    # 2. Caption sanitization (Anti-XSS)
    clean_caption = sanitize_input(caption)

    # 3. Database persistence
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO posts (user_id, image_url, caption, file_hash_sha256)
                VALUES (%s, %s, %s, %s)
            """, (user_id, image_url, clean_caption, file_sha256))
            post_id = cursor.lastrowid

            cursor.execute("SELECT created_at FROM posts WHERE id = %s", (post_id,))
            created_at = str(cursor.fetchone()["created_at"])

            log_audit_event(
                conn=conn,
                user_id=user_id,
                action_type="POST_CREATED",
                target_entity="POST",
                target_id=post_id,
                ip_address=client_ip,
                details=f"Post {post_id} created with image {image_url} (SHA256: {file_sha256[:16]}...)"
            )

    return PostResponse(
        id=post_id,
        user_id=user_id,
        username=current_user["username"],
        image_url=image_url,
        caption=clean_caption,
        file_hash_sha256=file_sha256,
        likes_count=0,
        comments_count=0,
        created_at=created_at
    )

@router.get("/feed", response_model=List[PostResponse])
def get_feed(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Query posts from followed users, public profiles, and self
            cursor.execute("""
                SELECT 
                    p.id, p.user_id, u.username, p.image_url, p.caption, 
                    p.file_hash_sha256, p.created_at,
                    (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS likes_count,
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comments_count
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE 
                    p.user_id = %s
                    OR u.is_private = FALSE
                    OR p.user_id IN (
                        SELECT followed_id FROM follows WHERE follower_id = %s
                    )
                ORDER BY p.created_at DESC
                LIMIT 50;
            """, (user_id, user_id))
            rows = cursor.fetchall()

            feed = []
            for row in rows:
                feed.append(PostResponse(
                    id=row["id"],
                    user_id=row["user_id"],
                    username=row["username"],
                    image_url=row["image_url"],
                    caption=row["caption"] or "",
                    file_hash_sha256=row["file_hash_sha256"],
                    likes_count=row["likes_count"],
                    comments_count=row["comments_count"],
                    created_at=str(row["created_at"])
                ))
            return feed

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.id, p.user_id, u.username, u.is_private, p.image_url, p.caption, 
                    p.file_hash_sha256, p.created_at,
                    (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS likes_count,
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comments_count
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.id = %s
            """, (post_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            # Privacy validation
            if row["is_private"] and row["user_id"] != current_user["user_id"]:
                cursor.execute(
                    "SELECT 1 FROM follows WHERE follower_id = %s AND followed_id = %s",
                    (current_user["user_id"], row["user_id"])
                )
                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access Denied: This account is private."
                    )

            return PostResponse(
                id=row["id"],
                user_id=row["user_id"],
                username=row["username"],
                image_url=row["image_url"],
                caption=row["caption"] or "",
                file_hash_sha256=row["file_hash_sha256"],
                likes_count=row["likes_count"],
                comments_count=row["comments_count"],
                created_at=str(row["created_at"])
            )

@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(
    post_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    client_ip = request.client.host if request.client else "unknown"

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, user_id, image_url FROM posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()

            if not post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            # CRITICAL ANTI-IDOR / ANTI-BOLA AUTHORIZATION CHECK
            if post["user_id"] != user_id and current_user["role"] != "admin":
                log_audit_event(
                    conn=conn,
                    user_id=user_id,
                    action_type="UNAUTHORIZED_DELETE_ATTEMPT",
                    target_entity="POST",
                    target_id=post_id,
                    ip_address=client_ip,
                    details=f"User {user_id} attempted unauthorized deletion of Post {post_id} owned by User {post['user_id']}"
                )
                conn.commit()
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access Denied: You do not have permission to delete this post."
                )

            # Proceed with deletion
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))

            # Clean up local file from disk safely
            local_filename = os.path.basename(post["image_url"])
            local_path = os.path.join(settings.UPLOAD_DIRECTORY, local_filename)
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception:
                    pass

            log_audit_event(
                conn=conn,
                user_id=user_id,
                action_type="POST_DELETED",
                target_entity="POST",
                target_id=post_id,
                ip_address=client_ip,
                details=f"Post {post_id} successfully deleted by owner {user_id}."
            )

    return MessageResponse(status="success", message=f"Post {post_id} deleted successfully.")
