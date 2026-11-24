from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from main import app, SECRET_KEY, ALGORITHM
from database import db


@pytest.fixture
def client():
    # Ensure tests use only the MongoDB testing database.
    assert db.name == "sentinelai_test", "Unsafe database!"

    with TestClient(app) as test_client:
        yield test_client


def create_expired_token():
    """Create a correctly signed JWT that has already expired."""

    now = datetime.now(timezone.utc)

    payload = {
        "sub": "tester",
        "iat": now - timedelta(minutes=10),
        "exp": now - timedelta(minutes=5),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def test_profile_rejects_invalid_jwt(client):
    """An invalid token must not access the user profile."""

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer invalid.fake.token"
        },
    )

    assert response.status_code == 401


def test_profile_rejects_expired_jwt(client):
    """An expired token must not access the user profile."""

    token = create_expired_token()

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_profile_rejects_wrong_signature(client):
    """A token signed with the wrong secret must be rejected."""

    payload = {
        "sub": "tester",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    wrong_token = jwt.encode(
        payload,
        "this-is-not-the-real-secret",
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {wrong_token}"
        },
    )

    assert response.status_code == 401


def test_profile_rejects_missing_token(client):
    """A request without an Authorization header must be rejected."""

    response = client.get("/api/auth/me")

    assert response.status_code in (401, 403)


def test_protected_threats_endpoint_rejects_invalid_jwt(client):
    """An invalid token must not access protected threat data."""

    response = client.get(
        "/api/rbac/threats",
        headers={
            "Authorization": "Bearer invalid.fake.token"
        },
    )

    assert response.status_code == 401