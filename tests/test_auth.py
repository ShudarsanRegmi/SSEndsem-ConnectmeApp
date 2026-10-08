import time
from fastapi.testclient import TestClient

def test_register_and_login_flow(client: TestClient):
    unique_suffix = int(time.time() * 1000)
    username = f"user_{unique_suffix}"
    email = f"user_{unique_suffix}@example.com"
    password = "SecurePassword123!"

    # 1. Register User
    reg_response = client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test User",
        "bio": "Security researcher"
    })
    assert reg_response.status_code == 201
    assert reg_response.json()["status"] == "success"

    # 2. Duplicate Registration Rejection
    dup_response = client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    assert dup_response.status_code == 409

    # 3. Successful Login
    login_response = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["username"] == username
    token = data["access_token"]

    # 4. Access Protected Profile
    me_response = client.get("/api/v1/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 200
    assert me_response.json()["username"] == username

def test_login_invalid_password(client: TestClient):
    unique_suffix = int(time.time() * 1000)
    username = f"fail_{unique_suffix}"
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "ValidPassword123"
    })

    bad_login = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "WrongPassword999"
    })
    assert bad_login.status_code == 401
    assert "Invalid username or password" in bad_login.json()["detail"]
