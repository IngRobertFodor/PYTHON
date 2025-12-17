# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_saucedemo
# python -m pytest

# OR
# RUN THIS TO RUN TESTS IN PARALLEL
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_saucedemo
# pip install pytest-xdist
# python -m pytest -n 2


from selenium import webdriver
import pytest
from pages.saucedemo_firstpage import SauceDemo_FirstPage
from pages.saucedemo_products_page import SauceDemo_ProductsPage


@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()

# Test Cases 1
def test_successful_login(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop_pp.webshop_productspage_title() == "Products"

# Test Cases 2
def test_locked_out_user(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("locked_out_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop_fp.webshop_lockedoutuser_error() == "Epic sadface: Sorry, this user has been locked out."

# Test Cases 3
def test_page_title(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    assert webshop_pp.webshop_productspage_title() == "Products"

# Test Cases 4
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

# Test Cases 5
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

# Test Cases 6
def test_about_menuitem_from_sidebar(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    webshop_pp.open_side_menu()
    assert webshop_pp.goto_about_menuitem_from_sidebar() == "https://saucelabs.com/"
    assert len(webshop_pp.text_about_menuitem_from_sidebar()) > 1
    for item in webshop_pp.text_about_menuitem_from_sidebar():
        if "mobile and web apps" in item:
            assert True
            break

# Test Cases 7
def test_dropdown_all_options(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    dropdown_items = webshop_pp.dropdown_all_options()
    assert len(dropdown_items) == 4
    assert dropdown_items[0] == "Name (A to Z)"
    for item in dropdown_items:
        if item in ["Name (A to Z)", "Name (Z to A)", "Price (low to high)", "Price (high to low)"]:
            assert True

# Test Cases 8
def test_add_first_item_to_cart(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    cart_count = webshop_pp.add_first_item_to_cart()
    assert cart_count == "1"
    assert cart_count != "0"