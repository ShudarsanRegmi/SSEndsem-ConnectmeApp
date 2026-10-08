import io
import time
from PIL import Image
from fastapi.testclient import TestClient

def get_auth_token(client: TestClient, username: str):
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "Password123!"
    })
    resp = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "Password123!"
    })
    return resp.json()["access_token"]

def generate_valid_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_genuine_image_upload_success(client: TestClient):
    suffix = int(time.time() * 1000)
    username = f"artist_{suffix}"
    token = get_auth_token(client, username)

    jpeg_bytes = generate_valid_jpeg_bytes()
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("my_photo.jpg", jpeg_bytes, "image/jpeg")},
        data={"caption": "Beautiful sunset in the mountains!"}
    )
    assert response.status_code == 201
    post = response.json()
    assert post["username"] == username
    assert post["caption"] == "Beautiful sunset in the mountains!"
    assert post["image_url"].startswith("/secure_media/")
    assert len(post["file_hash_sha256"]) == 64

def test_reject_php_webshell_disguised_as_jpg(client: TestClient):
    suffix = int(time.time() * 1000)
    username = f"hacker_{suffix}"
    token = get_auth_token(client, username)

    fake_image_bytes = b"<?php system($_GET['cmd']); ?>\r\nSome other text"
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("exploit.php.jpg", fake_image_bytes, "image/jpeg")},
        data={"caption": "Free gift card"}
    )
    assert response.status_code == 400
    assert "Security Violation" in response.json()["detail"] or "Invalid image format" in response.json()["detail"]

def test_reject_elf_executable(client: TestClient):
    suffix = int(time.time() * 1000)
    username = f"attacker_{suffix}"
    token = get_auth_token(client, username)

    elf_bytes = b"\x7FELF\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("binary.png", elf_bytes, "image/png")},
        data={"caption": "binary"}
    )
    assert response.status_code == 400
    assert "Security Violation" in response.json()["detail"]

def test_reject_oversized_image(client: TestClient):
    suffix = int(time.time() * 1000)
    username = f"bulk_{suffix}"
    token = get_auth_token(client, username)

    # 6MB payload (exceeds 5MB limit)
    oversized_bytes = b"\xFF\xD8\xFF" + (b"\x00" * (6 * 1024 * 1024))
    response = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("huge.jpg", oversized_bytes, "image/jpeg")},
        data={"caption": "too big"}
    )
    assert response.status_code == 413
