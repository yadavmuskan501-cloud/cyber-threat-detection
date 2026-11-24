import uuid

import pytest
from fastapi.testclient import TestClient

import main
from database import db, users_collection


@pytest.fixture
def client():
    assert db.name == "sentinelai_test", "Unsafe database!"

    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def login_user(client):

    assert db.name == "sentinelai_test"

    unique_id = uuid.uuid4().hex[:8]

    credentials = {
        "username": f"testanalyst_{unique_id}",
        "email": f"testanalyst_{unique_id}@example.com",
        "password": "SecureTest123!"
    }

    response = client.post(
        "/api/auth/register",
        json=credentials
    )

    assert response.status_code == 201

    try:
        yield credentials

    finally:
        assert db.name == "sentinelai_test"

        users_collection.delete_one(
            {"username": credentials["username"]}
        )


def test_valid_login_and_jwt_access(client, login_user):

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": login_user["username"],
            "password": login_user["password"]
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    assert token

    profile_response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert profile_response.status_code == 200

    assert (
        profile_response.json()["profile"]["username"]
        == login_user["username"]
    )


def test_login_rejects_wrong_password(client, login_user):

    response = client.post(
        "/api/auth/login",
        json={
            "username": login_user["username"],
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401

    assert "access_token" not in response.json()