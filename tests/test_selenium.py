
import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:8000"

TEST_USERNAME = "analyst2"
TEST_PASSWORD = "ExamplePass123!"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()

    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1366,900")

    browser = webdriver.Chrome(options=options)

    yield browser

    browser.quit()


def test_login_page_loads(driver):
    """Verify that the login page loads."""
    driver.get(BASE_URL)

    assert driver.title or "login" in driver.current_url.lower()


def test_successful_login(driver):
    """Verify successful login, JWT storage and dashboard redirect."""
    driver.get(BASE_URL)

    username_field = driver.find_element(By.ID, "loginUsername")
    password_field = driver.find_element(By.ID, "loginPassword")

    # Clear default HTML values
    username_field.clear()
    password_field.clear()

    username_field.send_keys(TEST_USERNAME)
    password_field.send_keys(TEST_PASSWORD)

    driver.find_element(By.ID, "loginBtn").click()

    wait = WebDriverWait(driver, 15)

    # Wait until the backend responds with a login result
    status_box = wait.until(
        EC.visibility_of_element_located((By.ID, "statusBox"))
    )

    # Check whether authentication succeeded
    if "AUTHENTICATED" not in status_box.text:
        pytest.fail(f"Login failed: {status_box.text}")

    # Verify that JWT and user details were stored
    token = driver.execute_script(
        "return sessionStorage.getItem('token');"
    )

    username = driver.execute_script(
        "return sessionStorage.getItem('username');"
    )

    role = driver.execute_script(
        "return sessionStorage.getItem('user_role');"
    )

    assert token is not None
    assert username == TEST_USERNAME
    assert role is not None

    # Wait for the 900ms delayed dashboard redirect
    wait.until(EC.url_contains("/dashboard"))


def test_invalid_login_shows_error(driver):
    """Verify that invalid credentials display an error."""
    driver.get(BASE_URL)

    username_field = driver.find_element(By.ID, "loginUsername")
    password_field = driver.find_element(By.ID, "loginPassword")

    username_field.clear()
    password_field.clear()

    username_field.send_keys("wronguser")
    password_field.send_keys("wrongpassword")

    driver.find_element(By.ID, "loginBtn").click()

    wait = WebDriverWait(driver, 10)

    status_box = wait.until(
        EC.visibility_of_element_located((By.ID, "statusBox"))
    )

    assert "ACCESS DENIED" in status_box.text
