
import pytest
import time

from datetime import datetime, timedelta, timezone
from jose import jwt

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test_selenium import (
    driver,
    BASE_URL,
    TEST_USERNAME,
    TEST_PASSWORD
)

from main import SECRET_KEY, ALGORITHM


def login_to_dashboard(browser):
    """Log in and wait for successful authentication and dashboard redirect."""

    browser.get(BASE_URL)

    username_field = browser.find_element(By.ID, "loginUsername")
    password_field = browser.find_element(By.ID, "loginPassword")

    username_field.clear()
    password_field.clear()

    username_field.send_keys(TEST_USERNAME)
    password_field.send_keys(TEST_PASSWORD)

    browser.find_element(By.ID, "loginBtn").click()

    wait = WebDriverWait(browser, 15)

    # Wait for the login response
    status_box = wait.until(
        EC.visibility_of_element_located((By.ID, "statusBox"))
    )

    if "AUTHENTICATED" not in status_box.text:
        pytest.fail(f"Login failed: {status_box.text}")

    # Verify that the authentication token was saved
    token = browser.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is not None, "Authentication token was not saved."

    # Wait for dashboard redirect
    wait.until(EC.url_contains("/dashboard"))

    # Wait until the username is displayed
    wait.until(
        lambda d: d.find_element(
            By.ID, "analystDisplay"
        ).text == f"Analyst: {TEST_USERNAME}"
    )


# --------------------------------------------------
# EXISTING DASHBOARD TESTS
# --------------------------------------------------

def test_dashboard_displays_username(driver):
    """Verify that the dashboard displays the logged-in username."""

    login_to_dashboard(driver)

    username = driver.find_element(
        By.ID, "analystDisplay"
    ).text

    assert username == f"Analyst: {TEST_USERNAME}"


def test_dashboard_displays_role(driver):
    """Verify that the dashboard displays the actual logged-in user's role."""

    login_to_dashboard(driver)

    wait = WebDriverWait(driver, 15)

    role_element = wait.until(
        EC.visibility_of_element_located((By.ID, "analystRole"))
    )

    assert role_element.text == "ROLE: ANALYST"


def test_dashboard_redirects_without_token(driver):
    """Verify that users without an authentication token are redirected."""

    driver.get(BASE_URL + "/dashboard")

    wait = WebDriverWait(driver, 10)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    assert driver.current_url == BASE_URL + "/"


def test_logout_clears_session_and_redirects(driver):
    """Verify logout clears the token and redirects to login."""

    login_to_dashboard(driver)

    logout_button = driver.find_element(
        By.XPATH, "//button[normalize-space()='Logout']"
    )

    logout_button.click()

    wait = WebDriverWait(driver, 10)

    # Wait for redirect to login page
    wait.until(EC.url_to_be(BASE_URL + "/"))

    # Verify that the token has been removed
    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is None, "Token was not cleared after logout."

    assert driver.current_url == BASE_URL + "/"


# --------------------------------------------------
# ADDITIONAL DASHBOARD SESSION SECURITY TESTS
# --------------------------------------------------

def test_dashboard_remains_authenticated_after_refresh(driver):
    """Verify that refreshing the dashboard preserves a valid session."""

    login_to_dashboard(driver)

    driver.refresh()

    wait = WebDriverWait(driver, 15)

    wait.until(EC.url_contains("/dashboard"))

    wait.until(
        lambda d: d.find_element(
            By.ID, "analystDisplay"
        ).text == f"Analyst: {TEST_USERNAME}"
    )

    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is not None, "Token was lost after dashboard refresh."


def test_dashboard_redirects_with_invalid_token(driver):
    """Verify that an invalid token causes a redirect to login."""

    driver.get(BASE_URL)

    driver.execute_script(
        "sessionStorage.setItem('token', 'invalid.fake.token');"
    )

    driver.get(BASE_URL + "/dashboard")

    wait = WebDriverWait(driver, 15)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is None, "Invalid token was not cleared."


def test_dashboard_redirects_with_expired_token(driver):
    """Verify that an expired JWT causes a redirect to login."""

    now = datetime.now(timezone.utc)

    payload = {
        "sub": TEST_USERNAME,
        "iat": now - timedelta(minutes=10),
        "exp": now - timedelta(minutes=5),
    }

    expired_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    driver.get(BASE_URL)

    driver.execute_script(
        "sessionStorage.setItem('token', arguments[0]);",
        expired_token,
    )

    driver.get(BASE_URL + "/dashboard")

    wait = WebDriverWait(driver, 15)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is None, "Expired token was not cleared."


def test_browser_back_after_logout_does_not_restore_session(driver):
    """Inspect browser Back behavior after logout."""

    login_to_dashboard(driver)

    # Log out
    driver.find_element(
        By.XPATH, "//button[normalize-space()='Logout']"
    ).click()

    wait = WebDriverWait(driver, 10)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    # Press browser Back
    driver.back()

    # Give browser history and dashboard JavaScript time to respond
    time.sleep(3)

    current_url = driver.current_url

    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    print("\nURL after browser Back:", current_url)
    print("Token after browser Back:", token)

    if "/dashboard" in current_url:
        print(
            "Dashboard page was restored. "
            "Checking whether authenticated data is visible."
        )

        try:
            username = driver.find_element(
                By.ID, "analystDisplay"
            ).text
        except Exception:
            username = "Dashboard username not visible"

        print("Dashboard username:", username)

    # The session must remain cleared even if browser restores the page.
    assert token is None, "Session was restored after logout."
