import pytest
from fastapi.testclient import TestClient

from main import app
from database import db


@pytest.fixture
def client():
    # Ensure tests use only the MongoDB testing database.
    assert db.name == "sentinelai_test", "Unsafe database!"

    with TestClient(app) as test_client:
        yield test_client


def test_app_starts(client):
    assert app is not None


def test_protected_profile_requires_authentication(client):

    response = client.get("/api/auth/me")

    assert response.status_code in (401, 403)