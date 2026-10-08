import io
import time
from PIL import Image
from fastapi.testclient import TestClient

def create_user_and_token(client: TestClient, prefix: str):
    suffix = int(time.time() * 1000)
    username = f"{prefix}_{suffix}"
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "Password123!"
    })
    resp = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "Password123!"
    })
    return username, resp.json()["access_token"]

def generate_test_jpeg():
    img = Image.new("RGB", (50, 50), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_prevent_idor_on_post_deletion(client: TestClient):
    # User A creates a post
    user_a, token_a = create_user_and_token(client, "alice")
    jpeg_data = generate_test_jpeg()

    post_resp = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"image": ("alice_art.jpg", jpeg_data, "image/jpeg")},
        data={"caption": "Alice exclusive artwork"}
    )
    assert post_resp.status_code == 201
    post_id = post_resp.json()["id"]

    # User B attempts to delete User A's post (BOLA / IDOR Attack Vector)
    user_b, token_b = create_user_and_token(client, "bob_attacker")

    malicious_del_resp = client.delete(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    # MUST BE REJECTED WITH 403 FORBIDDEN
    assert malicious_del_resp.status_code == 403
    assert "Access Denied" in malicious_del_resp.json()["detail"]

    # Verify post still exists in feed
    get_resp = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert get_resp.status_code == 200

    # User A (legitimate author) deletes the post
    legit_del_resp = client.delete(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert legit_del_resp.status_code == 200
    assert "deleted successfully" in legit_del_resp.json()["message"]

    # Verify post is now gone
    final_get = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert final_get.status_code == 404
