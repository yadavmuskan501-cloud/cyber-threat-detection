"""Alert logging for Sentinel AI (Future Scope prototype).

This module is self-contained: it uses only the standard library and does
not import or modify main.py, the ML code or the existing database.
Every function takes the database path as a parameter, so it can be
tested on a temporary file and wired into the API later (see
docs/FUTURE_SCOPE.md).
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional

DEFAULT_ALERTS_DB = "alerts.db"

SEVERITY_CRITICAL = "Critical"
SEVERITY_HIGH = "High"
SEVERITY_MEDIUM = "Medium"
SEVERITY_LOW = "Low"


def severity_from_confidence(confidence: float) -> str:
    """Map a model confidence score (0 to 1) to a severity level."""

    if not 0.0 <= confidence <= 1.0:
        raise ValueError("Confidence must be between 0 and 1.")

    if confidence >= 0.95:
        return SEVERITY_CRITICAL

    if confidence >= 0.85:
        return SEVERITY_HIGH

    if confidence >= 0.70:
        return SEVERITY_MEDIUM

    return SEVERITY_LOW


def init_alerts_table(db_path: str = DEFAULT_ALERTS_DB) -> None:
    """Create the alerts table if it does not exist."""

    conn = sqlite3.connect(db_path)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                severity TEXT NOT NULL,
                triggered_by TEXT NOT NULL
            )
        """)

        conn.commit()

    finally:
        conn.close()


def save_alert(
    prediction_result: dict,
    triggered_by: str,
    db_path: str = DEFAULT_ALERTS_DB
) -> Optional[int]:
    """Store an alert when the prediction is ATTACK.

    Takes the dict returned by ml.predict.predict_threat. Returns the new
    alert id, or None when the traffic was BENIGN and nothing was stored.
    """

    if prediction_result.get("prediction") != "ATTACK":
        return None

    confidence = float(prediction_result["confidence"])
    severity = severity_from_confidence(confidence)

    init_alerts_table(db_path)

    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.execute(
            """
            INSERT INTO alerts
            (created_at, prediction, confidence, severity, triggered_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                "ATTACK",
                confidence,
                severity,
                triggered_by
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def list_alerts(
    limit: int = 50,
    db_path: str = DEFAULT_ALERTS_DB
) -> list:
    """Return the most recent alerts, newest first."""

    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    init_alerts_table(db_path)

    conn = sqlite3.connect(db_path)

    try:
        rows = conn.execute(
            """
            SELECT id, created_at, prediction, confidence,
                   severity, triggered_by
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    finally:
        conn.close()

    return [
        {
            "id": row[0],
            "created_at": row[1],
            "prediction": row[2],
            "confidence": row[3],
            "severity": row[4],
            "triggered_by": row[5]
        }
        for row in rows
    ]
