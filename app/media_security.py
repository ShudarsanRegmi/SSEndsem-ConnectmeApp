import os
import io
import uuid
import hashlib
from typing import Tuple
from PIL import Image, ImageOps
from fastapi import HTTPException, UploadFile, status
from app.config import settings

# Recognized image magic numbers
MAGIC_SIGNATURES = {
    b"\xFF\xD8\xFF": ("image/jpeg", ".jpg"),
    b"\x89PNG\r\n\x1a\n": ("image/png", ".png"),
    b"RIFF": ("image/webp", ".webp")
}

# Dangerous executable signatures to immediately reject
REJECTED_SIGNATURES = [
    b"MZ",           # Windows PE
    b"\x7FELF",      # Linux ELF
    b"<?php",        # PHP Script
    b"<script",      # HTML/JS Script
    b"#!/bin/",      # Shell script
]

def ensure_upload_directory_exists():
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

async def validate_and_process_image(upload_file: UploadFile) -> Tuple[str, str]:
    ensure_upload_directory_exists()
    
    # Read entire payload into memory
    content = await upload_file.read()
    file_size = len(content)

    # 1. Enforce max file size
    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum permissible size of {settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024):.1f} MB"
        )
    if file_size < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty or corrupted."
        )

    # 2. Check for dangerous executable signatures
    for bad_sig in REJECTED_SIGNATURES:
        if content[:16].startswith(bad_sig) or bad_sig in content[:64].lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Violation: Executable or script binary detected."
            )

    # 3. Magic Byte Inspection
    detected_ext = None
    for magic, (mime_type, ext) in MAGIC_SIGNATURES.items():
        if content.startswith(magic):
            if magic == b"RIFF" and b"WEBP" not in content[:16]:
                continue
            detected_ext = ext
            break

    if not detected_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Only authentic JPEG, PNG, and WebP images are permitted."
        )

    # 4. Image Re-encoding & EXIF metadata stripping (Neutralizes polyglots & GPS metadata)
    try:
        image = Image.open(io.BytesIO(content))
        image.verify()  # Verifies file integrity
        
        # Re-open for stripping metadata and re-encoding
        image = Image.open(io.BytesIO(content))
        # Strip EXIF orientation & data
        image = ImageOps.exif_transpose(image)
        
        output_buffer = io.BytesIO()
        # Normalize to RGB if JPEG, RGBA if PNG
        if detected_ext in [".jpg", ".jpeg"]:
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(output_buffer, format="JPEG", quality=90, optimize=True)
        elif detected_ext == ".png":
            image.save(output_buffer, format="PNG", optimize=True)
        else:
            image.save(output_buffer, format="WEBP", quality=90)
            
        clean_content = output_buffer.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image decoding failed: File contains malformed image structures."
        )

    # 5. Calculate SHA-256 checksum
    file_sha256 = hashlib.sha256(clean_content).hexdigest()

    # 6. Generate cryptographically random UUID filename (Anti-path-traversal)
    safe_filename = f"{uuid.uuid4().hex}{detected_ext}"
    dest_path = os.path.join(settings.UPLOAD_DIRECTORY, safe_filename)

    # 7. Write to non-executable storage with restricted permissions
    with open(dest_path, "wb") as f:
        f.write(clean_content)

    os.chmod(dest_path, 0o644)  # Read/write for owner, read-only for others, no execution

    public_url = f"/secure_media/{safe_filename}"
    return public_url, file_sha256
