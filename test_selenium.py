
from selenium import webdriver
from selenium.webdriver.common.by import By


# Test 1: Home page
def test_home_page_selenium():
    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5000")

        assert "Cloud Backup" in driver.page_source

    finally:
        driver.quit()


# Test 2: Upload page
def test_upload_page_selenium():
    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5000/upload-page")

        assert "Upload Your Backup" in driver.page_source

    finally:
        driver.quit()


# Test 3: Backups page
def test_backups_page_selenium():
    driver = webdriver.Chrome()

    try:
        driver.get("http://127.0.0.1:5000/backups")

        assert "Your Backup History" in driver.page_source

    finally:
        driver.quit()
