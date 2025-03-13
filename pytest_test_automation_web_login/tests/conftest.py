import json
import pytest
from selenium import webdriver


@pytest.fixture
def config():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        return config


@pytest.fixture
def browser(config):
    if config["browser"] == "Firefox":
        browser = webdriver.Firefox()
    elif config["browser"] == "Chrome":
        browser = webdriver.Chrome()
    elif config["browser"] == "Headless Firefox":
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--headless")
        browser = webdriver.Firefox(firefox_options=firefox_options)
    elif config["browser"] == "Headless Chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=chrome_options)
    else:
        raise Exception("Browser from config file is not supported. Supported browsers are: Firefox, Chrome or Headless Firefox.")
    browser.implicitly_wait(config["implicit_wait"])
    yield browser
    browser.quit()