"""End-to-end tests for registration, login, refresh and logout."""


def test_register_creates_tester_by_default(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "newbie@example.com", "username": "newbie", "password": "Password123!"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["role"] == "tester"
    assert body["profile"]["xp_total"] == 0
    assert body["profile"]["level"] == 1


def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "username": "dupuser", "password": "Password123!"}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post(
        "/api/v1/auth/register",
        json={**payload, "username": "dupuser2"},
    )
    assert second.status_code == 400


def test_login_with_correct_credentials_returns_tokens(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "loginuser@example.com", "username": "loginuser", "password": "Password123!"},
    )
    resp = client.post(
        "/api/v1/auth/login", json={"email": "loginuser@example.com", "password": "Password123!"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "username": "wrongpass", "password": "Password123!"},
    )
    resp = client.post(
        "/api/v1/auth/login", json={"email": "wrongpass@example.com", "password": "WrongOne123!"}
    )
    assert resp.status_code == 401


def test_refresh_rotates_tokens(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "refresher@example.com", "username": "refresher", "password": "Password123!"},
    )
    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "refresher@example.com", "password": "Password123!"}
    )
    tokens = login_resp.json()

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # Old refresh token should now be revoked (rotation).
    reuse_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reuse_resp.status_code == 401


def test_logout_revokes_refresh_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "logout@example.com", "username": "logoutuser", "password": "Password123!"},
    )
    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "logout@example.com", "password": "Password123!"}
    )
    tokens = login_resp.json()

    logout_resp = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_resp.status_code == 200

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 401


def test_forgot_and_reset_password_flow(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "forgot@example.com", "username": "forgotuser", "password": "OldPassword123!"},
    )
    forgot_resp = client.post("/api/v1/auth/forgot-password", json={"email": "forgot@example.com"})
    assert forgot_resp.status_code == 200
    reset_token = forgot_resp.json()["reset_token_debug"]

    reset_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewPassword456!"},
    )
    assert reset_resp.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login", json={"email": "forgot@example.com", "password": "OldPassword123!"}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login", json={"email": "forgot@example.com", "password": "NewPassword456!"}
    )
    assert new_login.status_code == 200


def test_get_me_requires_auth(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_get_me_returns_profile(client, register_and_login):
    _, headers = register_and_login("meuser@example.com", "meuser", "Password123!")
    resp = client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "meuser@example.com"
    assert body["role"] == "tester"
