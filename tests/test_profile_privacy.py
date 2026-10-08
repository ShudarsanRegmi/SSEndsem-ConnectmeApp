import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_profile_update_and_xss_sanitization():
    # 1. Register a test user
    reg_payload = {
        "username": "profileuser1",
        "email": "profileuser1@connectme.io",
        "password": "Password123!"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login to get token
    login_res = client.post("/api/v1/auth/login", json={
        "username": "profileuser1",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Update profile with XSS payload in bio
    xss_bio = "<script>alert('pwned')</script> Hello World"
    update_res = client.put("/api/v1/users/me", json={
        "full_name": "Sanitized User",
        "bio": xss_bio,
        "is_private": False
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "success"

    # 4. Fetch own profile and verify HTML tags were escaped
    me_res = client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    profile_data = me_res.json()
    assert "<script>" not in profile_data["bio"]
    assert "&lt;script&gt;" in profile_data["bio"]
    assert profile_data["full_name"] == "Sanitized User"
    assert profile_data["is_private"] is False


def test_third_party_profile_email_masking():
    # 1. Register target user
    client.post("/api/v1/auth/register", json={
        "username": "targetuser",
        "email": "targetuser@connectme.io",
        "password": "Password123!"
    })
    login_target = client.post("/api/v1/auth/login", json={
        "username": "targetuser",
        "password": "Password123!"
    })
    target_id = login_target.json()["user_id"]

    # 2. Register viewer user
    client.post("/api/v1/auth/register", json={
        "username": "vieweruser",
        "email": "vieweruser@connectme.io",
        "password": "Password123!"
    })
    login_viewer = client.post("/api/v1/auth/login", json={
        "username": "vieweruser",
        "password": "Password123!"
    })
    viewer_token = login_viewer.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # 3. Viewer requests target's profile
    res = client.get(f"/api/v1/users/{target_id}", headers=viewer_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "targetuser"
    assert data["email"] == "[Protected]"
