
import uuid

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test_selenium import driver, BASE_URL


def test_invalid_login_shows_access_denied(driver):
    """Verify incorrect login credentials display ACCESS DENIED."""
    driver.get(BASE_URL)

    username = driver.find_element(By.ID, "loginUsername")
    password = driver.find_element(By.ID, "loginPassword")

    username.clear()
    username.send_keys("wrong_user")

    password.clear()
    password.send_keys("WrongPassword123")

    driver.find_element(By.ID, "loginBtn").click()

    status = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "statusBox"))
    )

    assert "ACCESS DENIED" in status.text


def test_empty_login_fields_are_rejected_by_browser(driver):
    """Verify browser validation rejects empty login fields."""
    driver.get(BASE_URL)

    driver.find_element(By.ID, "loginUsername").clear()
    driver.find_element(By.ID, "loginPassword").clear()

    login_form = driver.find_element(By.ID, "loginForm")

    is_valid = driver.execute_script(
        "return arguments[0].checkValidity();",
        login_form
    )

    assert is_valid is False


def test_invalid_email_is_rejected_by_browser(driver):
    """Verify browser validation rejects an invalid email."""
    driver.get(BASE_URL)

    driver.find_element(By.ID, "tabRegister").click()

    unique_id = uuid.uuid4().hex[:8]

    driver.find_element(By.ID, "regUsername").send_keys(
        f"email_{unique_id}"
    )
    driver.find_element(By.ID, "regEmail").send_keys("invalid-email")
    driver.find_element(By.ID, "regPassword").send_keys("Password123")

    register_form = driver.find_element(By.ID, "registerForm")

    is_valid = driver.execute_script(
        "return arguments[0].checkValidity();",
        register_form
    )

    assert is_valid is False


def test_weak_password_shows_error(driver):
    """Verify backend rejects passwords shorter than eight characters."""
    driver.get(BASE_URL)

    driver.find_element(By.ID, "tabRegister").click()

    unique_id = uuid.uuid4().hex[:8]

    driver.find_element(By.ID, "regUsername").send_keys(
        f"weak_{unique_id}"
    )
    driver.find_element(By.ID, "regEmail").send_keys(
        f"weak_{unique_id}@example.com"
    )
    driver.find_element(By.ID, "regPassword").send_keys("short")

    driver.find_element(By.ID, "regBtn").click()

    status = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "statusBox"))
    )

    assert "ERROR" in status.text
    assert "at least 8 characters" in status.text.lower()
