
import sqlite3

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a separate temporary database.
    monkeypatch.setattr(
        main,
        "DB_NAME",
        str(tmp_path / "rbac_test.db")
    )

    main.init_database()
    return TestClient(main.app)


def register_and_login(client, username, role=None):
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

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": "SecureTest123!"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_analyst_can_view_threats(client):
    token = register_and_login(
        client,
        "analyst_test"
    )

    response = client.get(
        "/api/rbac/threats",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_analyst_cannot_access_admin(client):
    token = register_and_login(
        client,
        "analyst_restricted"
    )

    response = client.get(
        "/api/rbac/admin",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_registration_cannot_assign_admin(client):
    token = register_and_login(
        client,
        "fake_admin",
        role="Admin"
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["profile"]["role"] == "Analyst"


def test_admin_can_access_admin_endpoint(client):
    # Set up a privileged user directly in the
    # isolated test database, not via public registration.
    with sqlite3.connect(main.DB_NAME) as conn:
        conn.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            ("Admin", "analyst1")
        )

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "analyst1",
            "password": "Sentinel2026!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

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


def test_analyst_cannot_view_users(client):
    token = register_and_login(
        client,
        "restricted_analyst"
    )

    response = client.get(
        "/api/rbac/users",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403
