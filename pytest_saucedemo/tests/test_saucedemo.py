# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_saucedemo
# python -m pytest


from selenium import webdriver
import pytest
from pages.saucedemo_firstpage import SauceDemo_FirstPage


@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()

def test_login(driver):
    webshop = SauceDemo_FirstPage(driver)
    webshop.load_page("https://www.saucedemo.com/")
    webshop.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop.webshop_firstpage_title() == "Products"