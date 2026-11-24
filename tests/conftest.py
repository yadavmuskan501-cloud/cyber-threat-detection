import json
import uuid
import pytest

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def test_account():
    """Automatically register a unique test account."""

    unique_id = uuid.uuid4().hex[:8]

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
            f"Cannot connect to Sentinel AI server: {error}"
        )

    return credentials