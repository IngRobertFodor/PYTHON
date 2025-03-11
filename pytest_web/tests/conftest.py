import json
import pytest
from selenium import webdriver


@pytest.fixture
def config():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    return config


@pytest.fixture
def driver(config):
    if config["browser"] == "Firefox":
        driver = webdriver.Firefox()
    elif config["browser"] == "Chrome":
        driver = webdriver.Chrome()
    elif config["browser"] == "Headless Firefox":
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--Headless")
        driver = webdriver.Firefox(options=firefox_options)
    else:
        raise Exception("Browser from config file is not supported. Supported browsers are: Firefox, Chrome, Headless Firefox")
    driver.implicitly_wait(config["implicit_wait"])
    yield driver
    driver.quit()