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
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop_pp.webshop_productspage_title() == "Products"

def test_locked_out_user(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("locked_out_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop_fp.webshop_lockedoutuser_error() == "Epic sadface: Sorry, this user has been locked out."

def test_page_title(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop_pp.webshop_productspage_title() == "Products"

def test_item_in_products(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    p_name = webshop_pp.get_products_list()
    assert "Sauce Labs Backpack" in p_name
    assert "Sauce Labs Backpacc" not in p_name
    assert len(p_name) == 6

@pytest.mark.parametrize("expected_count", [(5, 6)])
def test_number_of_items_in_products(driver, expected_count):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    p_name_len = webshop_pp.get_products_list()
    assert len(p_name_len) != expected_count[0]
    assert len(p_name_len) == expected_count[1]