"""Fixtures compartidos para pytest."""
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Forzar base en memoria y carpeta temporal antes de importar la app
os.environ["DATABASE_URL"] = "sqlite:///./test_agrovision.db"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="agrovision_test_")

from backend.database import Base, get_db  # noqa: E402
from backend.main import app  # noqa: E402

TEST_DB = "sqlite:///./test_agrovision.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


@pytest.fixture(scope="session", autouse=True)
def _create_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # 1. Eliminar las tablas
    Base.metadata.drop_all(bind=engine)
    # 2. Liberar las conexiones del motor
    engine.dispose()
    # 3. Eliminar el archivo de la base de datos
    db_file = Path("./test_agrovision.db")
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    client.post("/auth/register", json={
        "username": "admin_test", "email": "admin@test.com",
        "password": "admin1234", "role": "admin",
    })
    r = client.post("/auth/login", data={"username": "admin_test", "password": "admin1234"})
    return r.json()["access_token"]


@pytest.fixture
def user_token(client):
    client.post("/auth/register", json={
        "username": "user_test", "email": "user@test.com",
        "password": "user1234", "role": "usuario",
    })
    r = client.post("/auth/login", data={"username": "user_test", "password": "user1234"})
    return r.json()["access_token"]
