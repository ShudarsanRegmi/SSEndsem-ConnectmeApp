from fastapi import APIRouter, HTTPException, Request, status, Depends
from app.database import get_db
from app.models import UserRegisterRequest, UserLoginRequest, TokenResponse, MessageResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    login_rate_limiter,
    sanitize_input,
    log_audit_event,
    get_current_user
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    clean_username = payload.username.strip().lower()
    clean_email = payload.email.strip().lower()
    clean_full_name = sanitize_input(payload.full_name)
    clean_bio = sanitize_input(payload.bio)

    pwd_hash = hash_password(payload.password)

    with get_db() as conn:
        with conn.cursor() as cursor:
            # Check for existing username or email
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (clean_username, clean_email))
            existing = cursor.fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username or email is already registered."
                )

            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, bio, role)
                VALUES (%s, %s, %s, %s, %s, 'user')
            """, (clean_username, clean_email, pwd_hash, clean_full_name, clean_bio))
            new_user_id = cursor.lastrowid

            log_audit_event(
                conn=conn,
                user_id=new_user_id,
                action_type="USER_REGISTER",
                target_entity="USER",
                target_id=new_user_id,
                ip_address=client_ip,
                details=f"User {clean_username} registered."
            )

    return MessageResponse(status="success", message="User registered successfully.")

@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    
    # Apply rate limiting by client IP
    if not login_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: Too many failed login attempts. Try again later."
        )

    clean_username = payload.username.strip().lower()

    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = %s OR email = %s",
                (clean_username, clean_username)
            )
            user = cursor.fetchone()

            if not user or not verify_password(payload.password, user["password_hash"]):
                log_audit_event(
                    conn=conn,
                    user_id=None,
                    action_type="LOGIN_FAILED",
                    target_entity="USER",
                    target_id=None,
                    ip_address=client_ip,
                    details=f"Failed login attempt for identifier: {clean_username}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password."
                )

            # Issue JWT token
            token = create_access_token(
                user_id=user["id"],
                username=user["username"],
                role=user["role"]
            )

            log_audit_event(
                conn=conn,
                user_id=user["id"],
                action_type="LOGIN_SUCCESS",
                target_entity="USER",
                target_id=user["id"],
                ip_address=client_ip,
                details=f"User {user['username']} logged in successfully."
            )

            return TokenResponse(
                access_token=token,
                user_id=user["id"],
                username=user["username"],
                role=user["role"]
            )

@router.get("/me")
def get_current_authenticated_user(current_user: dict = Depends(get_current_user)):
    return current_user
