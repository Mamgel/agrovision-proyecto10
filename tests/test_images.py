import io
from PIL import Image


def _fake_image_bytes():
    img = Image.new("RGB", (640, 640), (34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_upload_and_analyze_without_model(client, admin_token):
    """La API debe responder incluso si no hay best.pt (modo simulado)."""
    h = {"Authorization": f"Bearer {admin_token}"}
    buf = _fake_image_bytes()
    r = client.post("/images", files={"file": ("hoja.jpg", buf, "image/jpeg")}, headers=h)
    assert r.status_code == 201
    img_id = r.json()["id"]

    r = client.post(f"/images/{img_id}/analyze", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["image_id"] == img_id
    assert body["n_leaves_detected"] >= 0
    assert body["model_version"]


def test_rejects_bad_extension(client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    r = client.post("/images", files={"file": ("doc.txt", io.BytesIO(b"xx"), "text/plain")}, headers=h)
    assert r.status_code == 400


def test_image_requires_auth(client):
    buf = _fake_image_bytes()
    r = client.post("/images", files={"file": ("x.jpg", buf, "image/jpeg")})
    assert r.status_code == 401
