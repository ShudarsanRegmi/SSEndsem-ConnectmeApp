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
    return resp.json()["user_id"], username, resp.json()["access_token"]

def generate_test_jpeg():
    img = Image.new("RGB", (40, 40), color="yellow")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_social_interactions_and_xss_sanitization(client: TestClient):
    uid_a, user_a, token_a = create_user_and_token(client, "creator")
    uid_b, user_b, token_b = create_user_and_token(client, "fan")

    # Creator creates post
    post_resp = client.post(
        "/api/v1/posts",
        headers={"Authorization": f"Bearer {token_a}"},
        files={"image": ("pic.jpg", generate_test_jpeg(), "image/jpeg")},
        data={"caption": "Check this out"}
    )
    post_id = post_resp.json()["id"]

    # 1. Fan likes post
    like_resp = client.post(
        f"/api/v1/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert like_resp.status_code == 200
    assert like_resp.json()["message"] == "Post liked."

    # 2. Fan unlikes post
    unlike_resp = client.post(
        f"/api/v1/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert unlike_resp.status_code == 200
    assert unlike_resp.json()["message"] == "Post unliked."

    # 3. Fan submits comment with potential Stored XSS payload
    xss_payload = "<script>alert('xss');</script><img src=x onerror=alert(1)>"
    comment_resp = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"comment_text": xss_payload}
    )
    assert comment_resp.status_code == 201
    sanitized_comment = comment_resp.json()["comment_text"]
    # Verify that raw script tags are neutralized
    assert "<script>" not in sanitized_comment
    assert "&lt;script&gt;" in sanitized_comment

    # 4. Fan follows Creator
    follow_resp = client.post(
        f"/api/v1/users/{uid_a}/follow",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert follow_resp.status_code == 200
    assert "Successfully followed" in follow_resp.json()["message"]

    # 5. Prevent Self-Follow
    self_follow = client.post(
        f"/api/v1/users/{uid_b}/follow",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert self_follow.status_code == 400
    assert "cannot follow yourself" in self_follow.json()["detail"]
