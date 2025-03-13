# IN CMD:

# PATH where to run my test:
# C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_login

# RUN THIS
# python -m pytest


from pages.the_internet_herokuapp import Web_Page


def test_web_login(browser):

    username = "tomsmith"
    password = "SuperSecretPassword!"

    expected_web_page = Web_Page(browser)

    # Given the "the-internet.herokuapp.com" web page is displayed
    expected_web_page.load_page()

    # When the user clicks on the "Form Authentication" link
    expected_web_page.login_link_find().click()
    
    # Then user type the username
    expected_web_page.username_field().send_keys(username)
    
    # And user type the password
    expected_web_page.password_field().send_keys(password)

    # And user clicks on the "Login" button
    expected_web_page.login_button().click()
    
    # And user checkes displayed message
    assert expected_web_page.popup_message() == "You logged into a secure area!"
