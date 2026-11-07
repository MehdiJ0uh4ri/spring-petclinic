"""Place at e2e/test_register_pet.py.

User journey: create an owner, then register a new pet for that owner.
"""
import os
import random
import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
HERE = os.path.dirname(os.path.abspath(__file__))


def _rand(n=6):
    return "".join(random.choices(string.ascii_lowercase, k=n))


def _driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,1000")
    return webdriver.Chrome(options=opts)  # Selenium Manager fetches the driver


def _fill(driver, field_id, value):
    el = driver.find_element(By.ID, field_id)
    el.clear()
    el.send_keys(value)


def test_register_new_pet():
    driver = _driver()
    wait = WebDriverWait(driver, 20)
    pet_name = f"Rex{_rand()}"
    try:
        # 1. Create an owner
        driver.get(f"{BASE_URL}/owners/new")
        _fill(driver, "firstName", "Ada")
        _fill(driver, "lastName", f"Tester{_rand()}")
        _fill(driver, "address", "1 Pipeline Street")
        _fill(driver, "city", "Nantes")
        _fill(driver, "telephone", "0612345678")
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        wait.until(EC.url_matches(r"/owners/\d+$"))

        # 2. Open the "Add New Pet" form
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Add New Pet"))).click()
        wait.until(EC.url_contains("/pets/new"))

        # 3. Fill the pet form (date input set via JS: sendKeys is locale-dependent)
        _fill(driver, "name", pet_name)
        driver.execute_script(
            "arguments[0].value = arguments[1];",
            driver.find_element(By.ID, "birthDate"),
            "2022-03-15",
        )
        Select(driver.find_element(By.ID, "type")).select_by_visible_text("cat")
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

        # 4. Back on the owner page, the new pet must be listed
        wait.until(EC.url_matches(r"/owners/\d+$"))
        body = driver.find_element(By.TAG_NAME, "body").text
        assert pet_name in body, f"Pet {pet_name!r} not found on owner page:\n{body}"
    except Exception:
        driver.save_screenshot(os.path.join(HERE, "failure.png"))
        raise
    finally:
        driver.quit()
