def test_register_and_login_flow(client):
    # 1. Register
    reg_resp = client.post("/api/auth/register", json={
        "email": "candidate@hireme.com",
        "password": "StrongPassword123!"
    })
    assert reg_resp.status_code == 201
    assert "user" in reg_resp.get_json()

    # 2. Duplicate registration fails
    dup_resp = client.post("/api/auth/register", json={
        "email": "candidate@hireme.com",
        "password": "StrongPassword123!"
    })
    assert dup_resp.status_code == 409

    # 3. Weak password fails
    weak_resp = client.post("/api/auth/register", json={
        "email": "weak@hireme.com",
        "password": "short"
    })
    assert weak_resp.status_code == 400

    # 4. Successful Login
    login_resp = client.post("/api/auth/login", json={
        "email": "candidate@hireme.com",
        "password": "StrongPassword123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()["access_token"]
    assert token is not None

    # 5. Invalid credentials fail
    bad_login = client.post("/api/auth/login", json={
        "email": "candidate@hireme.com",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 6. Authenticated user profile (/api/auth/me)
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.get_json()["user"]["email"] == "candidate@hireme.com"

    # 7. Unauthenticated access fails
    unauth_resp = client.get("/api/auth/me")
    assert unauth_resp.status_code == 401
