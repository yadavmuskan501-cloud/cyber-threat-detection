import pytest
import time

from datetime import datetime, timedelta, timezone
from jose import jwt

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test_selenium import driver, BASE_URL

from main import SECRET_KEY, ALGORITHM


def login_to_dashboard(browser, test_account):
    """Log in using an automatically registered test account."""

    browser.get(BASE_URL)

    username_field = browser.find_element(By.ID, "loginUsername")
    password_field = browser.find_element(By.ID, "loginPassword")

    username_field.clear()
    password_field.clear()

    username_field.send_keys(test_account["username"])
    password_field.send_keys(test_account["password"])

    browser.find_element(By.ID, "loginBtn").click()

    wait = WebDriverWait(browser, 15)

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "statusBox"), "AUTHENTICATED"
        )
    )

    token = browser.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is not None, "Authentication token was not saved."

    wait.until(EC.url_contains("/dashboard"))

    wait.until(
        lambda d: d.find_element(
            By.ID, "analystDisplay"
        ).text == f"Analyst: {test_account['username']}"
    )


# --------------------------------------------------
# DASHBOARD TESTS
# --------------------------------------------------

def test_dashboard_displays_username(driver, test_account):
    """Verify that the dashboard displays the logged-in username."""

    login_to_dashboard(driver, test_account)

    username = driver.find_element(
        By.ID, "analystDisplay"
    ).text

    assert username == f"Analyst: {test_account['username']}"


def test_dashboard_displays_role(driver, test_account):
    """Verify that the dashboard displays the actual user role."""

    login_to_dashboard(driver, test_account)

    wait = WebDriverWait(driver, 15)

    role_element = wait.until(
        EC.visibility_of_element_located((By.ID, "analystRole"))
    )

    assert role_element.text == "ROLE: ANALYST"


def test_dashboard_redirects_without_token(driver):
    """Verify that unauthenticated users are redirected."""

    driver.get(BASE_URL + "/dashboard")

    wait = WebDriverWait(driver, 10)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    assert driver.current_url == BASE_URL + "/"


def test_logout_clears_session_and_redirects(driver, test_account):
    """Verify that logout clears the token and redirects to login."""

    login_to_dashboard(driver, test_account)

    logout_button = driver.find_element(
        By.XPATH, "//button[normalize-space()='Logout']"
    )

    logout_button.click()

    wait = WebDriverWait(driver, 10)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is None, "Token was not cleared after logout."
    assert driver.current_url == BASE_URL + "/"


# --------------------------------------------------
# DASHBOARD SESSION SECURITY TESTS
# --------------------------------------------------

def test_dashboard_remains_authenticated_after_refresh(
    driver, test_account
):
    """Verify that refreshing preserves a valid session."""

    login_to_dashboard(driver, test_account)

    driver.refresh()

    wait = WebDriverWait(driver, 15)

    wait.until(EC.url_contains("/dashboard"))

    wait.until(
        lambda d: d.find_element(
            By.ID, "analystDisplay"
        ).text == f"Analyst: {test_account['username']}"
    )

    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    assert token is not None, "Token was lost after refresh."


def test_dashboard_redirects_with_invalid_token(driver):
    """Verify that an invalid token redirects to login."""

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


def test_dashboard_redirects_with_expired_token(driver, test_account):
    """Verify that an expired JWT redirects to login."""

    now = datetime.now(timezone.utc)

    payload = {
        "sub": test_account["username"],
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


def test_browser_back_after_logout_does_not_restore_session(
    driver, test_account
):
    """Inspect browser Back behavior after logout."""

    login_to_dashboard(driver, test_account)

    driver.find_element(
        By.XPATH, "//button[normalize-space()='Logout']"
    ).click()

    wait = WebDriverWait(driver, 10)

    wait.until(EC.url_to_be(BASE_URL + "/"))

    driver.back()

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

    assert token is None, "Session was restored after logout."