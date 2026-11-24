from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from main import app, create_access_token
from database import db


@pytest.fixture
def client():
    assert db.name == "sentinelai_test", "Unsafe database!"

    with TestClient(app) as test_client:
        yield test_client


def test_profile_rejects_invalid_token(client):

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer invalid-test-token"
        }
    )

    assert response.status_code in (401, 403)


def test_expired_jwt_token_rejected(client):

    expired_token = create_access_token(
        data={"sub": "expired_test_user"},
        expires_delta=timedelta(seconds=-10)
    )

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401