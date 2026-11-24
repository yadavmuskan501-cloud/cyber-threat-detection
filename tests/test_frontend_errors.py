import uuid

from database import db, users_collection

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from test_selenium import driver, BASE_URL


def test_invalid_login_shows_access_denied(driver):
    """Verify invalid login credentials display an error."""

    driver.get(BASE_URL)

    driver.find_element(By.ID, "loginUsername").send_keys("wronguser")
    driver.find_element(By.ID, "loginPassword").send_keys("wrongpassword")
    driver.find_element(By.ID, "loginBtn").click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "statusBox"), "ACCESS DENIED"
        )
    )


def test_empty_login_fields_rejected(driver):
    """Verify browser validation rejects empty login fields."""

    driver.get(BASE_URL)

    login_form = driver.find_element(By.ID, "loginForm")

    is_valid = driver.execute_script(
        "return arguments[0].checkValidity();",
        login_form
    )

    assert is_valid is False


def test_invalid_email_rejected(driver):
    """Verify browser validation rejects an invalid email."""

    driver.get(BASE_URL)

    driver.find_element(By.ID, "tabRegister").click()

    unique_id = uuid.uuid4().hex[:8]

    driver.find_element(By.ID, "regUsername").send_keys(
        f"selenium_{unique_id}"
    )

    driver.find_element(By.ID, "regEmail").send_keys(
        "invalid-email"
    )

    driver.find_element(By.ID, "regPassword").send_keys(
        "SecurePass123!"
    )

    register_form = driver.find_element(By.ID, "registerForm")

    is_valid = driver.execute_script(
        "return arguments[0].checkValidity();",
        register_form
    )

    assert is_valid is False


def test_weak_password_shows_backend_error(driver):
    """Verify backend rejects a password that is too short."""

    driver.get(BASE_URL)

    driver.find_element(By.ID, "tabRegister").click()

    unique_id = uuid.uuid4().hex[:8]

    driver.find_element(By.ID, "regUsername").send_keys(
        f"selenium_{unique_id}"
    )

    driver.find_element(By.ID, "regEmail").send_keys(
        f"selenium_{unique_id}@example.com"
    )

    driver.find_element(By.ID, "regPassword").send_keys("123")

    driver.find_element(By.ID, "regBtn").click()

    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.ID, "statusBox"), "ERROR"
        )
    )


def test_registration_tab_opens(driver):
    """Verify clicking Register opens the registration form."""

    driver.get(BASE_URL)

    driver.find_element(By.ID, "tabRegister").click()

    register_form = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.ID, "registerForm")
        )
    )

    assert register_form.is_displayed()


def test_successful_registration(driver):
    """Verify successful registration and clean up the test user."""

    assert db.name == "sentinelai_test", "Unsafe database!"

    unique_id = uuid.uuid4().hex
    username = f"selenium_{unique_id}"
    email = f"{username}@example.com"
    password = "SecurePass123!"

    try:
        driver.get(BASE_URL)

        driver.find_element(By.ID, "tabRegister").click()

        driver.find_element(
            By.ID, "regUsername"
        ).send_keys(username)

        driver.find_element(
            By.ID, "regEmail"
        ).send_keys(email)

        driver.find_element(
            By.ID, "regPassword"
        ).send_keys(password)

        register_form = driver.find_element(
            By.ID, "registerForm"
        )

        is_valid = driver.execute_script(
            "return arguments[0].checkValidity();",
            register_form
        )

        assert is_valid

        driver.find_element(By.ID, "regBtn").click()

        login_form = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(
                (By.ID, "loginForm")
            )
        )

        assert login_form.is_displayed()

        registered_username = driver.find_element(
            By.ID, "loginUsername"
        ).get_attribute("value")

        assert registered_username == username

        assert users_collection.find_one({
            "username": username,
            "email": email
        }) is not None

    finally:
        users_collection.delete_one({
            "username": username,
            "email": email
        })