# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_saucedemo
# python -m pytest

# OR
# RUN THIS - RUN TESTS IN PARALLEL
# pip install pytest-xdist
# python -m pytest -n 2

# OR
# RUN THIS - RUN TESTS IN PARALLEL and FOR MORE DETAILED OUTPUT
# python -m pytest -n 2 --verbose

# OR
# RUN THIS - RUN TESTS IN PARALLEL and FOR MORE DETAILED OUTPUT and TO RUN EXACT TEST (e.g. # Test Cases 1: test_successful_login)
# python -m pytest -n 2 --verbose -k test_successful_login


from selenium import webdriver
import pytest
from pages.saucedemo_firstpage import SauceDemo_FirstPage
from pages.saucedemo_productspage import SauceDemo_ProductsPage
from pages.saucedemo_shoppingcartpage import SauceDemo_ShoppingCartPage


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

# Test Cases 4
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

# Test Cases 5
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

# Test Cases 6
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

# Test Cases 7
def test_shopping_cart_item_count(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    webshop_pp.add_first_item_to_cart()
    cart_count = webshop_pp.shopping_cart_item_count_number()
    assert cart_count == "1"
    webshop_pp.back_to_products_page()
    webshop_pp.add_second_item_to_cart()
    cart_count = webshop_pp.shopping_cart_item_count_number()
    assert cart_count == "2"

# Test Cases 8
def test_review_shopping_cart(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_scp = SauceDemo_ShoppingCartPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    webshop_pp.add_first_item_to_cart()
    webshop_pp.back_to_products_page()
    webshop_pp.add_second_item_to_cart()
    webshop_pp.click_shopping_cart()
    cart_items_list = webshop_scp.review_shopping_cart()
    assert len(cart_items_list) == 2
    assert "Sauce Labs Backpack" in cart_items_list
    assert "Sauce Labs Fleece Jacket" in cart_items_list

# Test Cases 9
def test_remove_first_item_from_shopping_cart(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_scp = SauceDemo_ShoppingCartPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    webshop_pp.add_first_item_to_cart()
    webshop_pp.back_to_products_page()
    webshop_pp.add_second_item_to_cart()
    webshop_scp.remove_first_item_from_shopping_cart()
    cart_count = webshop_pp.shopping_cart_item_count_number()
    assert cart_count == "1"

# Test Cases 10
def test_proceed_to_checkout(driver):
    webshop_fp = SauceDemo_FirstPage(driver)
    webshop_pp = SauceDemo_ProductsPage(driver)
    webshop_scp = SauceDemo_ShoppingCartPage(driver)
    webshop_fp.load_page("https://www.saucedemo.com/")
    webshop_fp.login("standard_user", "secret_sauce")
    driver.implicitly_wait(10)
    webshop_pp.add_first_item_to_cart()
    webshop_pp.back_to_products_page()
    webshop_pp.add_second_item_to_cart()
    webshop_scp.remove_first_item_from_shopping_cart()
    webshop_pp.click_shopping_cart()
    webshop_scp.proceed_to_checkout()
    assert driver.current_url == "https://www.saucedemo.com/checkout-step-one.html"
    webshop_scp.form_filling_checkout_information("", "Doe", "12345")
    assert webshop_scp.error_message_checkout_information() == "Error: First Name is required"
    webshop_scp.cancel_checkout()
    webshop_scp.proceed_to_checkout()
    webshop_scp.form_filling_checkout_information("John", "", "12345")
    assert webshop_scp.error_message_checkout_information() == "Error: Last Name is required"
    webshop_scp.cancel_checkout()
    webshop_scp.proceed_to_checkout()
    webshop_scp.form_filling_checkout_information("John", "Doe", "")
    assert webshop_scp.error_message_checkout_information() == "Error: Postal Code is required"
    webshop_scp.cancel_checkout()
    webshop_scp.proceed_to_checkout()
    webshop_scp.form_filling_checkout_information("John", "Doe", "12345")
    assert driver.current_url == "https://www.saucedemo.com/checkout-step-two.html"