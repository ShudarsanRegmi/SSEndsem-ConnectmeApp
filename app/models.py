from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field("", max_length=100)
    bio: Optional[str] = Field("", max_length=300)

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    bio: str
    profile_pic_url: str
    is_private: bool
    role: str
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=300)
    profile_pic_url: Optional[str] = Field(None, max_length=255)
    is_private: Optional[bool] = None

class PostResponse(BaseModel):
    id: int
    user_id: int
    username: str
    image_url: str
    caption: str
    file_hash_sha256: str
    likes_count: int
    comments_count: int
    created_at: str

class CommentCreateRequest(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=500)

class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    username: str
    comment_text: str
    created_at: str

class MessageResponse(BaseModel):
    status: str
    message: str
