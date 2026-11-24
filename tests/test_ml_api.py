import uuid

import pytest
from fastapi.testclient import TestClient

import main
from database import db, users_collection
from ml.predict import load_model


@pytest.fixture
def client():
    assert db.name == "sentinelai_test", "Unsafe database!"

    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    unique_id = uuid.uuid4().hex[:8]
    username = f"ml_test_{unique_id}"

    credentials = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "MLTestPass123!"
    }

    try:
        response = client.post(
            "/api/auth/register",
            json=credentials
        )

        assert response.status_code == 201, response.text

        token = main.create_access_token(
            {"sub": username}
        )

        yield {
            "Authorization": f"Bearer {token}"
        }

    finally:
        users_collection.delete_one(
            {"username": username}
        )


@pytest.fixture
def valid_features():
    artifact = load_model()

    return {
        feature: None
        for feature in artifact["features"]
    }


def test_valid_prediction(client, auth_headers, valid_features):
    response = client.post(
        "/api/ml/predict",
        headers=auth_headers,
        json={"features": valid_features}
    )

    assert response.status_code == 200, response.text

    result = response.json()["result"]

    assert result["prediction"] in ("BENIGN", "ATTACK")
    assert result["prediction_code"] in (0, 1)
    assert 0 <= result["confidence"] <= 1


def test_missing_jwt(client, valid_features):
    response = client.post(
        "/api/ml/predict",
        json={"features": valid_features}
    )

    assert response.status_code in (401, 403)


def test_invalid_jwt(client, valid_features):
    response = client.post(
        "/api/ml/predict",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        json={"features": valid_features}
    )

    assert response.status_code in (401, 403)


def test_missing_features(client, auth_headers, valid_features):
    valid_features.pop(next(iter(valid_features)))

    response = client.post(
        "/api/ml/predict",
        headers=auth_headers,
        json={"features": valid_features}
    )

    assert response.status_code == 400


def test_unknown_features(client, auth_headers, valid_features):
    valid_features["unknown_feature"] = 123

    response = client.post(
        "/api/ml/predict",
        headers=auth_headers,
        json={"features": valid_features}
    )

    assert response.status_code == 400