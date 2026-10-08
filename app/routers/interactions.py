from fastapi import APIRouter, HTTPException, Depends, Request, status
from typing import List
from app.database import get_db
from app.models import CommentCreateRequest, CommentResponse, MessageResponse
from app.security import get_current_user, sanitize_input, log_audit_event

router = APIRouter(prefix="/api/v1", tags=["Interactions"])

@router.post("/posts/{post_id}/like", response_model=MessageResponse)
def toggle_like(post_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Check if post exists
            cursor.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            cursor.execute("SELECT id FROM likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
            existing_like = cursor.fetchone()

            if existing_like:
                cursor.execute("DELETE FROM likes WHERE id = %s", (existing_like["id"],))
                return MessageResponse(status="success", message="Post unliked.")
            else:
                cursor.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
                return MessageResponse(status="success", message="Post liked.")

@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: int,
    payload: CommentCreateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    client_ip = request.client.host if request.client else "unknown"

    # Strict Anti-XSS Sanitization on Comment Field (CWE-79 Remediation)
    clean_text = sanitize_input(payload.comment_text.strip())
    if not clean_text or len(clean_text) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment cannot be blank.")

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

            cursor.execute("""
                INSERT INTO comments (user_id, post_id, comment_text)
                VALUES (%s, %s, %s)
            """, (user_id, post_id, clean_text))
            comment_id = cursor.lastrowid

            cursor.execute("SELECT created_at FROM comments WHERE id = %s", (comment_id,))
            created_at = str(cursor.fetchone()["created_at"])

            log_audit_event(
                conn=conn,
                user_id=user_id,
                action_type="COMMENT_ADDED",
                target_entity="COMMENT",
                target_id=comment_id,
                ip_address=client_ip,
                details=f"User {user_id} commented on Post {post_id}"
            )

    return CommentResponse(
        id=comment_id,
        post_id=post_id,
        user_id=user_id,
        username=current_user["username"],
        comment_text=clean_text,
        created_at=created_at
    )

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(post_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.post_id, c.user_id, u.username, c.comment_text, c.created_at
                FROM comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.post_id = %s
                ORDER BY c.created_at ASC
            """, (post_id,))
            rows = cursor.fetchall()
            return [
                CommentResponse(
                    id=r["id"],
                    post_id=r["post_id"],
                    user_id=r["user_id"],
                    username=r["username"],
                    comment_text=r["comment_text"],
                    created_at=str(r["created_at"])
                ) for r in rows
            ]

@router.post("/users/{target_user_id}/follow", response_model=MessageResponse)
def follow_user(target_user_id: int, current_user: dict = Depends(get_current_user)):
    follower_id = current_user["user_id"]
    if follower_id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Action: You cannot follow yourself."
        )

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (target_user_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            cursor.execute("""
                SELECT id FROM follows WHERE follower_id = %s AND followed_id = %s
            """, (follower_id, target_user_id))
            if cursor.fetchone():
                return MessageResponse(status="success", message="Already following this user.")

            cursor.execute("""
                INSERT INTO follows (follower_id, followed_id)
                VALUES (%s, %s)
            """, (follower_id, target_user_id))

    return MessageResponse(status="success", message="Successfully followed user.")

@router.post("/users/{target_user_id}/unfollow", response_model=MessageResponse)
def unfollow_user(target_user_id: int, current_user: dict = Depends(get_current_user)):
    follower_id = current_user["user_id"]
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM follows WHERE follower_id = %s AND followed_id = %s
            """, (follower_id, target_user_id))
    return MessageResponse(status="success", message="Successfully unfollowed user.")
