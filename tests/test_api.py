
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_app_starts():
    assert app is not None


def test_protected_profile_requires_authentication():
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)
