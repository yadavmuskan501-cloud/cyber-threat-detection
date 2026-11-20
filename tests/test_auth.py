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