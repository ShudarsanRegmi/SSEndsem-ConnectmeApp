import io
import time
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_user_with_token(username: str, is_private: bool = False):
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "Password123!"
    })
    login_resp = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "Password123!"
    })
    token = login_resp.json()["access_token"]
    user_id = login_resp.json()["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    if is_private:
        client.put("/api/v1/users/me", json={"is_private": True}, headers=headers)

    return user_id, token, headers

def upload_dummy_post(headers: dict, caption: str):
    img = Image.new("RGB", (50, 50), color="purple")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = client.post(
        "/api/v1/posts",
        headers=headers,
        files={"image": ("post.jpg", buf.getvalue(), "image/jpeg")},
        data={"caption": caption}
    )
    return res.json()

def test_follow_and_unfollow_workflow():
    ts = int(time.time() * 1000)
    user1_id, _, headers1 = create_user_with_token(f"user1_{ts}")
    user2_id, _, headers2 = create_user_with_token(f"user2_{ts}")

    # 1. User 1 cannot follow themselves
    self_res = client.post(f"/api/v1/users/{user1_id}/follow", headers=headers1)
    assert self_res.status_code == 400
    assert "cannot follow yourself" in self_res.json()["detail"]

    # 2. User 1 follows User 2
    follow_res = client.post(f"/api/v1/users/{user2_id}/follow", headers=headers1)
    assert follow_res.status_code == 200
    assert follow_res.json()["status"] == "success"

    # 3. Check User 2 profile shows 1 follower
    profile_res = client.get(f"/api/v1/users/{user2_id}", headers=headers1)
    assert profile_res.status_code == 200
    assert profile_res.json()["followers_count"] == 1

    # 4. User 1 unfollows User 2
    unfollow_res = client.post(f"/api/v1/users/{user2_id}/unfollow", headers=headers1)
    assert unfollow_res.status_code == 200
    assert unfollow_res.json()["status"] == "success"

    # 5. Check User 2 profile shows 0 followers
    profile_res2 = client.get(f"/api/v1/users/{user2_id}", headers=headers1)
    assert profile_res2.json()["followers_count"] == 0


def test_feed_privacy_and_reverse_chronological_delivery():
    ts = int(time.time() * 1000)
    # Creator with private account
    creator_id, _, creator_headers = create_user_with_token(f"creator_{ts}", is_private=True)
    post_private = upload_dummy_post(creator_headers, "Exclusive secret post")

    # Regular viewer
    viewer_id, _, viewer_headers = create_user_with_token(f"viewer_{ts}", is_private=False)

    # 1. Unfollowed: viewer feed must NOT contain creator's private post
    feed1 = client.get("/api/v1/posts/feed", headers=viewer_headers).json()
    post_ids1 = [p["id"] for p in feed1]
    assert post_private["id"] not in post_ids1

    # 2. Viewer follows the creator
    client.post(f"/api/v1/users/{creator_id}/follow", headers=viewer_headers)

    # 3. Followed: viewer feed MUST now contain creator's private post
    feed2 = client.get("/api/v1/posts/feed", headers=viewer_headers).json()
    post_ids2 = [p["id"] for p in feed2]
    assert post_private["id"] in post_ids2

    # 4. Viewer unfollows the creator
    client.post(f"/api/v1/users/{creator_id}/unfollow", headers=viewer_headers)

    # 5. Unfollowed again: creator's private post is excluded from feed
    feed3 = client.get("/api/v1/posts/feed", headers=viewer_headers).json()
    post_ids3 = [p["id"] for p in feed3]
    assert post_private["id"] not in post_ids3
