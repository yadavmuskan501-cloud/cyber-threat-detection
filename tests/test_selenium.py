import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from database import db


BASE_URL = "http://127.0.0.1:8001"


@pytest.fixture
def driver():
    """Create and close a Chrome browser for each test."""

    assert db.name == "sentinelai_test", "Unsafe database!"

    options = webdriver.ChromeOptions()

    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1366,900")

    browser = webdriver.Chrome(options=options)

    try:
        yield browser

    finally:
        browser.quit()


def test_login_page_loads(driver):
    """Verify that the login page loads correctly."""

    driver.get(BASE_URL)

    assert driver.current_url == BASE_URL + "/"

    login_form = driver.find_element(
        By.ID, "loginForm"
    )

    assert login_form.is_displayed()


def test_successful_login(driver, test_account):
    """Verify login using an automatically registered account."""

    driver.get(BASE_URL)

    username_field = driver.find_element(
        By.ID, "loginUsername"
    )

    password_field = driver.find_element(
        By.ID, "loginPassword"
    )

    username_field.clear()
    password_field.clear()

    username_field.send_keys(
        test_account["username"]
    )

    password_field.send_keys(
        test_account["password"]
    )

    driver.find_element(By.ID, "loginBtn").click()

    wait = WebDriverWait(driver, 15)

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "statusBox"),
            "AUTHENTICATED"
        )
    )

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
    assert username == test_account["username"]
    assert role == "Analyst"

    wait.until(
        EC.url_contains("/dashboard")
    )

    assert "/dashboard" in driver.current_url


def test_invalid_login_shows_error(driver):
    """Verify that invalid credentials display an error."""

    driver.get(BASE_URL)

    username_field = driver.find_element(
        By.ID, "loginUsername"
    )

    password_field = driver.find_element(
        By.ID, "loginPassword"
    )

    username_field.clear()
    password_field.clear()

    username_field.send_keys("wronguser")
    password_field.send_keys("wrongpassword")

    driver.find_element(By.ID, "loginBtn").click()

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "statusBox"),
            "ACCESS DENIED"
        )
    )