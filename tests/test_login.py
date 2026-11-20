
import pytest
from fastapi.testclient import TestClient
import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a temporary database for this test
    monkeypatch.setattr(
        main, "DB_NAME", str(tmp_path / "test_sentinel.db")
    )
    main.init_database()

    return TestClient(main.app)


def test_valid_login_and_jwt_access(client):
    # Register a test user
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "testanalyst",
            "email": "testanalyst@example.com",
            "password": "SecureTest123!",
            "role": "Analyst"
        }
    )

    assert register_response.status_code == 201

    # Login using correct credentials
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "testanalyst",
            "password": "SecureTest123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    assert token

    # Access protected profile using JWT
    profile_response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert profile_response.status_code == 200
    assert (
        profile_response.json()["profile"]["username"]
        == "testanalyst"
    )


def test_login_rejects_wrong_password(client):
    # Try login with an incorrect password
    response = client.post(
        "/api/auth/login",
        json={
            "username": "analyst1",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
