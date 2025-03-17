from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Web_Page:

    def __init__(self, browser):
        self.browser = browser

    def load_page(self):
        self.browser.get("https://the-internet.herokuapp.com/")
    
    def click_link(self):
        return self.browser.find_element(By.LINK_TEXT, "Inputs")
    
    def page_title_text(self):
        title_text = self.browser.find_element(By.XPATH, "//*[@class='large-6 small-12 columns large-centered']/h3").text
        return title_text
    
    def input_field_text(self, my_input):
        input_field = self.browser.find_element(By.XPATH, "//*[@class='example']/input")
        input_field.send_keys(my_input)
        return input_field.get_attribute("value")