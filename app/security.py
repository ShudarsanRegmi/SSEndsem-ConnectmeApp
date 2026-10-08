import time
import html
import bcrypt
import jwt
from typing import Optional, Dict
from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(user_id: int, username: str, role: str) -> str:
    now = int(time.time())
    expire = now + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": expire
    }
    encoded = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded

def decode_access_token(token: str) -> Dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please re-authenticate."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )

def sanitize_input(text: Optional[str]) -> str:
    if not text:
        return ""
    # Strip dangerous HTML and script tags to prevent Stored XSS
    return html.escape(text.strip(), quote=True)

class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.records: Dict[str, list] = {}

    def is_allowed(self, client_key: str) -> bool:
        if settings.APP_ENV in ["test", "testing"]:
            return True
        current_time = time.time()
        timestamps = self.records.get(client_key, [])
        # Keep only timestamps within window
        valid_timestamps = [t for t in timestamps if current_time - t < self.window_seconds]
        if len(valid_timestamps) >= self.max_requests:
            self.records[client_key] = valid_timestamps
            return False
        valid_timestamps.append(current_time)
        self.records[client_key] = valid_timestamps
        return True

# Default rate limiter for login (5 requests per 60 seconds per IP)
login_rate_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing Bearer Token"
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = int(payload.get("sub"))
    username = payload.get("username")
    role = payload.get("role")
    return {"user_id": user_id, "username": username, "role": role}

def log_audit_event(conn, user_id: Optional[int], action_type: str, target_entity: str, target_id: Optional[int], ip_address: str, details: str = ""):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action_type, target_entity, target_id, ip_address, details)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, action_type, target_entity, target_id, ip_address, details))
