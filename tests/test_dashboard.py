
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test_selenium import (
    driver,
    BASE_URL,
    TEST_USERNAME,
    TEST_PASSWORD
)


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
