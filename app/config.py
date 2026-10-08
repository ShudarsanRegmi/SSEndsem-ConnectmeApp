import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database Settings (MySQL default)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "aparichit")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "letmelogin")
    DB_NAME: str = os.getenv("DB_NAME", "connectme_db")

    # Cryptographic JWT Settings
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", 
        "8f4e2b1c6d9a0e5f7a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Media Storage Settings
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "./secure_media")
    MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", "5242880")) # 5MB

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
