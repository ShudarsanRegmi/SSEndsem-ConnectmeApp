from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.database import get_db
from app.models import UserProfileResponse, ProfileUpdateRequest, MessageResponse
from app.security import get_current_user, sanitize_input, log_audit_event

router = APIRouter(prefix="/api/v1/users", tags=["Profile"])

@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, bio, profile_pic_url, is_private, role
                FROM users WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # Metrics
            cursor.execute("SELECT COUNT(*) AS c FROM follows WHERE followed_id = %s", (user_id,))
            followers_count = cursor.fetchone()["c"]

            cursor.execute("SELECT COUNT(*) AS c FROM follows WHERE follower_id = %s", (user_id,))
            following_count = cursor.fetchone()["c"]

            cursor.execute("SELECT COUNT(*) AS c FROM posts WHERE user_id = %s", (user_id,))
            posts_count = cursor.fetchone()["c"]

            return UserProfileResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                full_name=user["full_name"] or "",
                bio=user["bio"] or "",
                profile_pic_url=user["profile_pic_url"] or "",
                is_private=bool(user["is_private"]),
                role=user["role"],
                followers_count=followers_count,
                following_count=following_count,
                posts_count=posts_count
            )

@router.put("/me", response_model=MessageResponse)
def update_my_profile(
    payload: ProfileUpdateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    client_ip = request.client.host if request.client else "unknown"

    with get_db() as conn:
        with conn.cursor() as cursor:
            updates = []
            params = []

            if payload.full_name is not None:
                updates.append("full_name = %s")
                params.append(sanitize_input(payload.full_name))

            if payload.bio is not None:
                updates.append("bio = %s")
                params.append(sanitize_input(payload.bio))

            if payload.profile_pic_url is not None:
                updates.append("profile_pic_url = %s")
                params.append(payload.profile_pic_url.strip())

            if payload.is_private is not None:
                updates.append("is_private = %s")
                params.append(payload.is_private)

            if not updates:
                return MessageResponse(status="success", message="No fields to update.")

            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, tuple(params))

            log_audit_event(
                conn=conn,
                user_id=user_id,
                action_type="PROFILE_UPDATED",
                target_entity="USER",
                target_id=user_id,
                ip_address=client_ip,
                details="User updated profile details."
            )

    return MessageResponse(status="success", message="Profile updated successfully.")

@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(user_id: int, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, bio, profile_pic_url, is_private, role
                FROM users WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # Metrics
            cursor.execute("SELECT COUNT(*) AS c FROM follows WHERE followed_id = %s", (user_id,))
            followers_count = cursor.fetchone()["c"]

            cursor.execute("SELECT COUNT(*) AS c FROM follows WHERE follower_id = %s", (user_id,))
            following_count = cursor.fetchone()["c"]

            cursor.execute("SELECT COUNT(*) AS c FROM posts WHERE user_id = %s", (user_id,))
            posts_count = cursor.fetchone()["c"]

            # Email confidentiality for third parties
            user_email = user["email"] if user_id == current_user["user_id"] else "[Protected]"

            return UserProfileResponse(
                id=user["id"],
                username=user["username"],
                email=user_email,
                full_name=user["full_name"] or "",
                bio=user["bio"] or "",
                profile_pic_url=user["profile_pic_url"] or "",
                is_private=bool(user["is_private"]),
                role=user["role"],
                followers_count=followers_count,
                following_count=following_count,
                posts_count=posts_count
            )
