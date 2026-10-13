import pytest
from fastapi.testclient import TestClient

from app.sqlite import init_db
from app.main import app


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Cada test usa una BD vacía en una carpeta temporal."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    init_db()


@pytest.fixture
def client():
    return TestClient(app)