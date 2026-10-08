import os
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, profile, posts, interactions

app = FastAPI(
    title="ConnectMe Secure Social API",
    description="Secure Social Media Platform with Strict Authentication, Authorization, File Validation, and Anti-IDOR Protections",
    version="1.0.0"
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://connectme.internal"
]

# Hardened CORS Policy (Remediates CWE-942 Wildcard CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Custom Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; "
        "object-src 'none';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Initialize Database Schema on Application Startup
@app.on_event("startup")
def on_startup():
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization postponed: {e}")

# Mount Static Secure Media Directory
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
app.mount("/secure_media", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="secure_media")

# Include Application Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(posts.router)
app.include_router(interactions.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "ConnectMe Secure API",
        "environment": settings.APP_ENV
    }

# Mount Built React Frontend Single Page Application
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

