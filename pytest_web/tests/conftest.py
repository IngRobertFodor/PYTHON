import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


@pytest.fixture
def my_browser():
    options = Options()
    options.binary_location = r"C:/Program Files/Mozilla Firefox/firefox.exe"
    driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()