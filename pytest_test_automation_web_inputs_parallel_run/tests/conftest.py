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
        firefox_options.add_argument("--Headless")
        browser = webdriver.Firefox(options=firefox_options)
    elif config["browser"] == "Headless Chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--Headless")
        browser = webdriver.Chrome(options=chrome_options)
    else:
        raise Exception(f'Browser "{config["browser"]}" is not supported')
    browser.implicitly_wait(config["implicit_wait"])
    yield browser
    browser.quit()