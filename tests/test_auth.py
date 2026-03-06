def test_register_success(client):
    payload = {
        "username": "user1",
        "email": "user1@test.com",
        "password": "123456"
    }
    response = client.post("/register", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user1"
    assert data["email"] == "user1@test.com"


def test_register_duplicate_username(client):
    payload = {
        "username": "user1",
        "email": "user1@test.com",
        "password": "123456"
    }
    client.post("/register", json=payload)
    response = client.post("/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_login_success(client):
    client.post("/register", json={
        "username": "user2",
        "email": "user2@test.com",
        "password": "123456"
    })

    response = client.post(
        "/login",
        data={"username": "user2", "password": "123456"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/login",
        data={"username": "wrong", "password": "wrong"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"