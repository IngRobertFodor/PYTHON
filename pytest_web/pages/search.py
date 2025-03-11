from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class DuckDuckSearchPages:

    def __init__(self, driver):
        self.driver = driver
    
    def load_page(self):
        self.driver.get("https://duckduckgo.com/")

    def search_phrase(self, phrase):
        search_box = self.driver.find_element(By.XPATH, "//*[@class='searchbox_searchbox__bfbmv']/input")
        search_box.send_keys(phrase)
        search_box.send_keys(Keys.RETURN)