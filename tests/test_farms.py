def test_farm_crud(client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = client.post("/farms", json={"name": "Finca A", "location": "Valle", "area_ha": 12.5}, headers=h)
    assert r.status_code == 201
    farm_id = r.json()["id"]

    r = client.get("/farms", headers=h)
    assert r.status_code == 200
    assert any(f["id"] == farm_id for f in r.json())

    r = client.get(f"/farms/{farm_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["name"] == "Finca A"


def test_user_cannot_create_farm(client, user_token):
    h = {"Authorization": f"Bearer {user_token}"}
    r = client.post("/farms", json={"name": "X"}, headers=h)
    assert r.status_code == 403


def test_lot_requires_farm(client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = client.post("/lots", json={"farm_id": 99999, "name": "L1"}, headers=h)
    assert r.status_code == 404
