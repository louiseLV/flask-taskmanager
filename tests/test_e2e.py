# tests/test_e2e.py
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="module", autouse=True)
def setup_user():
    """Créer un utilisateur test avant tous les tests E2E."""
    requests.post(
        BASE_URL + "/register",
        data={"username": "louise", "password": "secret", "confirm": "secret"},
    )


@pytest.fixture(scope="module")
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    yield driver
    driver.quit()


def test_login_flow(browser):
    browser.get(BASE_URL + "/login")

    # Remplir le formulaire
    browser.find_element(By.NAME, "username").send_keys("louise")
    browser.find_element(By.NAME, "password").send_keys("secret")
    browser.find_element(By.TAG_NAME, "button").click()

    # Attendre que la page d'accueil soit chargée
    WebDriverWait(browser, 5).until(lambda d: d.current_url.endswith("/"))

    assert browser.current_url.endswith("/")


def test_create_task_from_ui(browser):
    browser.get(BASE_URL + "/tasks/new")

    # Attendre que le formulaire soit présent
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.NAME, "title"))
    )

    browser.find_element(By.NAME, "title").send_keys("Write Selenium test")
    browser.find_element(By.NAME, "description").send_keys("E2E test created via UI")
    browser.find_element(By.TAG_NAME, "button").click()

    # Attendre que la tâche apparaisse sur la page d'accueil
    WebDriverWait(browser, 5).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Write Selenium test")
    )

    assert "Write Selenium test" in browser.page_source


def test_toggle_task_from_ui(browser):
    browser.get(BASE_URL + "/")

    # Attendre que le bouton toggle soit présent
    toggle_buttons = WebDriverWait(browser, 5).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "form[action*='toggle'] button")
        )
    )

    assert len(toggle_buttons) > 0

    toggle_buttons[0].click()

    # Attendre le message flash
    WebDriverWait(browser, 5).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Task status updated")
    )

    assert "Task status updated" in browser.page_source
