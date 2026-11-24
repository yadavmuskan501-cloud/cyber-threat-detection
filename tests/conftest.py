import os
import json
import uuid
import pytest

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# Always use the dedicated testing environment.
os.environ["SENTINEL_ENV"] = "test"

BASE_URL = "http://127.0.0.1:8001"


def pytest_sessionstart(session):
    """Prevent automated tests from using application data."""

    from database import db, init_database

    if db.name != "sentinelai_test":
        pytest.exit(
            "Unsafe database detected. Testing stopped.",
            returncode=1
        )

    init_database()

    print("\nTest database verified:", db.name)


@pytest.fixture(scope="session")
def test_account():
    """Register and automatically clean up a test account."""

    from database import db, users_collection

    assert db.name == "sentinelai_test", "Unsafe database!"

    unique_id = uuid.uuid4().hex

    credentials = {
        "username": f"selenium_{unique_id}",
        "email": f"selenium_{unique_id}@example.com",
        "password": "SeleniumTest123!"
    }

    request = Request(
        f"{BASE_URL}/api/auth/register",
        data=json.dumps(credentials).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=15) as response:
            assert response.status == 201

    except HTTPError as error:
        pytest.fail(
            f"Test account registration failed: "
            f"{error.code} - {error.read().decode()}"
        )

    except URLError as error:
        pytest.fail(
            f"Cannot connect to Sentinel AI test server: {error}"
        )

    account_filter = {
        "username": credentials["username"],
        "email": credentials["email"]
    }

    assert users_collection.find_one(account_filter), (
        "Registered account not found in MongoDB test database."
    )

    try:
        yield credentials

    finally:
        result = users_collection.delete_one(account_filter)

        print(
            "\nTest accounts removed:",
            result.deleted_count
        )