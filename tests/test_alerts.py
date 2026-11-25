"""Unit tests for alerts.py (no server or browser required)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import alerts  # noqa: E402


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / "alerts_test.db")


@pytest.mark.parametrize("confidence, expected", [
    (1.0, "Critical"),
    (0.95, "Critical"),
    (0.90, "High"),
    (0.85, "High"),
    (0.75, "Medium"),
    (0.70, "Medium"),
    (0.50, "Low"),
    (0.0, "Low"),
])
def test_severity_levels(confidence, expected):
    assert alerts.severity_from_confidence(confidence) == expected


@pytest.mark.parametrize("bad_value", [-0.1, 1.1])
def test_severity_rejects_invalid_confidence(bad_value):
    with pytest.raises(ValueError):
        alerts.severity_from_confidence(bad_value)


def test_attack_is_saved(db):
    result = {"prediction": "ATTACK", "prediction_code": 1, "confidence": 0.97}

    alert_id = alerts.save_alert(result, "analyst1", db)

    assert alert_id is not None

    stored = alerts.list_alerts(db_path=db)

    assert len(stored) == 1
    assert stored[0]["severity"] == "Critical"
    assert stored[0]["triggered_by"] == "analyst1"
    assert stored[0]["confidence"] == 0.97


def test_benign_is_not_saved(db):
    result = {"prediction": "BENIGN", "prediction_code": 0, "confidence": 0.99}

    assert alerts.save_alert(result, "analyst1", db) is None
    assert alerts.list_alerts(db_path=db) == []


def test_list_is_newest_first_and_respects_limit(db):
    for confidence in (0.60, 0.80, 0.99):
        alerts.save_alert(
            {"prediction": "ATTACK", "confidence": confidence},
            "analyst1",
            db
        )

    newest_two = alerts.list_alerts(limit=2, db_path=db)

    assert [a["confidence"] for a in newest_two] == [0.99, 0.80]


def test_list_rejects_invalid_limit(db):
    with pytest.raises(ValueError):
        alerts.list_alerts(limit=0, db_path=db)
