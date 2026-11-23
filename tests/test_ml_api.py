
import sqlite3

import pytest
from fastapi.testclient import TestClient

import main
from ml.predict import load_model


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a temporary database, not the real sentinel.db
    test_db = tmp_path / "test_sentinel.db"

    conn = sqlite3.connect(test_db)
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            role TEXT
        )
    """)
    conn.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        (1, "ml_test_analyst", "test@example.com", main.ROLE_ANALYST)
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(main, "DB_NAME", str(test_db))

    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    token = main.create_access_token(
        {"sub": "ml_test_analyst"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_features():
    artifact = load_model()

    # Valid feature names, with missing numeric values
    # handled by the trained imputer.
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
        headers={"Authorization": "Bearer invalid-token"},
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
