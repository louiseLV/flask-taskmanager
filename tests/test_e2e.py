# tests/test_e2e.py
import time
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="module", autouse=True)
def setup_user():
    """Créer un utilisateur test avant tous les tests E2E."""
    requests.post(
        BASE_URL + "/register",
        data={"username": "louise", "password": "secret", "confirm": "secret"},
    )
    time.sleep(0.5)


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

    browser.find_element(By.NAME, "username").send_keys("louise")
    browser.find_element(By.NAME, "password").send_keys("secret")
    browser.find_element(By.TAG_NAME, "button").click()

    time.sleep(1)

    assert browser.current_url.endswith("/")


def test_create_task_from_ui(browser):
    browser.get(BASE_URL + "/login")
    browser.find_element(By.NAME, "username").send_keys("louise")
    browser.find_element(By.NAME, "password").send_keys("secret")
    browser.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(browser, 5).until(lambda d: d.current_url.endswith("/"))

    browser.get(BASE_URL + "/tasks/new")
    WebDriverWait(browser, 5).until(lambda d: d.find_element(By.NAME, "title"))
    browser.find_element(By.NAME, "title").send_keys("Write Selenium test")
    browser.find_element(By.NAME, "description").send_keys("E2E test created via UI")
    browser.find_element(By.TAG_NAME, "button").click()

    WebDriverWait(browser, 5).until(lambda d: "Write Selenium test" in d.page_source)


def test_toggle_task_from_ui(browser):
    # login
    browser.get(BASE_URL + "/login")
    browser.find_element(By.NAME, "username").send_keys("louise")
    browser.find_element(By.NAME, "password").send_keys("secret")
    browser.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(browser, 5).until(lambda d: d.current_url.endswith("/"))

    # créer une tâche si elle n'existe pas
    browser.get(BASE_URL + "/tasks/new")
    browser.find_element(By.NAME, "title").send_keys("Task for toggle")
    browser.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(browser, 5).until(lambda d: "Task for toggle" in d.page_source)

    # toggle
    browser.get(BASE_URL + "/")
    toggle_buttons = browser.find_elements(By.CSS_SELECTOR, "form[action*='toggle'] button")
    assert len(toggle_buttons) > 0
    toggle_buttons[0].click()
    WebDriverWait(browser, 5).until(lambda d: "Task status updated" in d.page_source)
