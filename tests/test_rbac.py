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
def create_test_user(client):
    created_users = []

    def create_user(username, role=None, promote=False):

        assert db.name == "sentinelai_test"

        username = f"{username}_{uuid.uuid4().hex[:8]}"

        registration = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "SecureTest123!"
        }

        if role:
            registration["role"] = role

        response = client.post(
            "/api/auth/register",
            json=registration
        )

        assert response.status_code == 201

        created_users.append(username)

        if promote:
            result = users_collection.update_one(
                {"username": username},
                {"$set": {"role": "Admin"}}
            )

            assert result.modified_count == 1

        login_response = client.post(
            "/api/auth/login",
            json={
                "username": username,
                "password": "SecureTest123!"
            }
        )

        assert login_response.status_code == 200

        return login_response.json()["access_token"]

    yield create_user

    # Remove only accounts created by this fixture.
    assert db.name == "sentinelai_test"

    if created_users:
        users_collection.delete_many(
            {"username": {"$in": created_users}}
        )


def test_analyst_can_view_threats(client, create_test_user):

    token = create_test_user("analyst_test")

    response = client.get(
        "/api/rbac/threats",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_analyst_cannot_access_admin(client, create_test_user):

    token = create_test_user("analyst_restricted")

    response = client.get(
        "/api/rbac/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_registration_cannot_assign_admin(client, create_test_user):

    token = create_test_user(
        "fake_admin",
        role="Admin"
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["profile"]["role"] == "Analyst"


def test_admin_can_access_admin_endpoint(client, create_test_user):

    token = create_test_user(
        "admin_test",
        promote=True
    )

    response = client.get(
        "/api/rbac/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_admin_endpoint_requires_authentication(client):

    response = client.get("/api/rbac/admin")

    assert response.status_code in (401, 403)


def test_threats_endpoint_requires_authentication(client):

    response = client.get("/api/rbac/threats")

    assert response.status_code in (401, 403)


def test_analyst_cannot_view_users(client, create_test_user):

    token = create_test_user("restricted_analyst")

    response = client.get(
        "/api/rbac/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403