def test_register_user_success(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "SecurePassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Doe"
    assert "password" not in data["user"]

def test_register_duplicate_email(client):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "Password123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_login_success(client):
    user_info = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "MySecretPassword1"
    }
    client.post("/api/auth/register", json=user_info)

    login_resp = client.post("/api/auth/login", json={
        "email": "loginuser@example.com",
        "password": "MySecretPassword1"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

def test_login_invalid_password(client):
    user_info = {
        "name": "Wrong Pass User",
        "email": "wrongpass@example.com",
        "password": "CorrectPassword"
    }
    client.post("/api/auth/register", json=user_info)

    login_resp = client.post("/api/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "WrongPassword"
    })
    assert login_resp.status_code == 401

def test_get_me_endpoint(client, auth_headers):
    me_resp = client.get("/api/auth/me", headers=auth_headers)
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["email"] == "pilot@example.com"
    assert data["name"] == "Test Pilot"

def test_get_me_unauthorized(client):
    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 401

