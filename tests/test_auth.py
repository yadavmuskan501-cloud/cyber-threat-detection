from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_profile_rejects_invalid_token():
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer invalid-test-token"
        }
    )

    assert response.status_code in (401, 403)
    
    
from datetime import timedelta
from main import create_access_token


def test_expired_jwt_token_rejected():
    expired_token = create_access_token(
        data={"sub": "analyst1"},
        expires_delta=timedelta(seconds=-10)
    )

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401
