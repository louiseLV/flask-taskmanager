import time
import pytest
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://127.0.0.1:5001"


@pytest.fixture(scope="module")
def server():
    proc = subprocess.Popen(
        ["python3", "app.py", "--port", "5001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )   

    # attend que le serveur soit prêt
    timeout = 10  # secondes max
    start = time.time()
    while True:
        try:
            requests.get("http://127.0.0.1:5001/login")
            break  # serveur prêt
        except requests.ConnectionError:
            if time.time() - start > timeout:
                proc.terminate()
                proc.wait()
                raise RuntimeError("Server did not start in time")
            time.sleep(0.5)

    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="module")
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    yield driver
    driver.quit()


def test_login_flow(browser, server):
    browser.get(BASE_URL + "/login")

    username = browser.find_element(By.NAME, "username")
    password = browser.find_element(By.NAME, "password")
    submit = browser.find_element(By.TAG_NAME, "button")

    username.send_keys("louise")
    password.send_keys("secret")
    submit.click()

    time.sleep(1)

    assert browser.current_url.endswith("/")


def test_create_task_from_ui(browser, server):
    browser.get(BASE_URL + "/tasks/new")

    title = browser.find_element(By.NAME, "title")
    description = browser.find_element(By.NAME, "description")
    submit = browser.find_element(By.TAG_NAME, "button")

    title.send_keys("Write Selenium test")
    description.send_keys("E2E test created via UI")
    submit.click()

    time.sleep(1)

    page_source = browser.page_source
    assert "Write Selenium test" in page_source


def test_toggle_task_from_ui(browser, server):
    browser.get(BASE_URL + "/")

    toggle_buttons = browser.find_elements(
        By.CSS_SELECTOR, "form[action*='toggle'] button"
    )

    assert len(toggle_buttons) > 0

    first_button = toggle_buttons[0]
    first_button.click()

    time.sleep(1)

    assert "Task status updated" in browser.page_source
