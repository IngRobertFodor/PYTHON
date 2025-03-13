from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Web_Page:

    def __init__(self, browser):
        self.browser = browser

    def load_page(self):
        self.browser.get("https://the-internet.herokuapp.com/")

    def login_link_find(self):
        return self.browser.find_element(By.LINK_TEXT, "Form Authentication")

    def username_field(self):
        return self.browser.find_element(By.ID, "username")
    
    def password_field(self):
        return self.browser.find_element(By.ID, "password")

    def login_button(self):
        return self.browser.find_element(By.CLASS_NAME, "radius")
    
    def popup_message(self):
        pop_up_text = self.browser.find_element(By.ID, "flash-messages").text
        if "You logged into a secure area!" in pop_up_text:
            return "You logged into a secure area!"