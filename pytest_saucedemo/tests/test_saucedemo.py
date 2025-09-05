# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_saucedemo
# python -m pytest


from selenium import webdriver
import pytest
from pages.saucedemo_firstpage import SauceDemo_FirstPage
from pages.saucedemo_products_page import SauceDemo_ProductsPage


@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()

def test_successful_login(driver):
    webshop = SauceDemo_FirstPage(driver)
    webshop.load_page("https://www.saucedemo.com/")
    webshop.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop.webshop_productspage_title() == "Products"

def test_locked_out_user(driver):
    webshop = SauceDemo_FirstPage(driver)
    webshop.load_page("https://www.saucedemo.com/")
    webshop.login("locked_out_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop.webshop_lockedoutuser_error() == "Epic sadface: Sorry, this user has been locked out."

def test_item_in_products(driver):
    webshop = SauceDemo_FirstPage(driver)
    webshop.load_page("https://www.saucedemo.com/")
    webshop.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop.webshop_productspage_title() == "Products"

def test_locked_out_user(driver):
    webshop = SauceDemo_FirstPage(driver)
    webshop.load_page("https://www.saucedemo.com/")
    webshop.login("locked_out_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop.webshop_lockedoutuser_error() == "Epic sadface: Sorry, this user has been locked out."

def test_item_in_products(driver):
    webshop = SauceDemo_FirstPage(driver)
    webshop.load_page("https://www.saucedemo.com/")
    webshop.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    products_page = SauceDemo_ProductsPage(driver)
    product_names = products_page.get_product_names()
    assert "Sauce Labs Backpack" in product_names
    assert "Sauce Labs Backpacc" not in product_names  