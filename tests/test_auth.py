def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


def test_register_and_login(client):
    r = client.post("/auth/register", json={
        "username": "pepe", "email": "pepe@mail.com", "password": "secret1", "role": "usuario"
    })
    assert r.status_code == 201
    r = client.post("/auth/login", data={"username": "pepe", "password": "secret1"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_invalid(client):
    r = client.post("/auth/login", data={"username": "nope", "password": "x"})
    assert r.status_code == 401


def test_register_duplicate(client):
    client.post("/auth/register", json={
        "username": "dup", "email": "dup@mail.com", "password": "secret1", "role": "usuario"
    })
    r = client.post("/auth/register", json={
        "username": "dup", "email": "dup2@mail.com", "password": "secret1", "role": "usuario"
    })
    assert r.status_code == 400


def test_me_requires_token(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_token(client, user_token):
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "user_test"
