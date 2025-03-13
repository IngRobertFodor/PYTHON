from selenium.webdriver.common.by import By


class DuckDuckResultPages:

    def __init__(self, browser):
        self.browser = browser

    def search_input_value(self):
        search_input = self.browser.find_element(By.XPATH, "//*[@id='search_form']/input")
        return search_input.get_attribute("value")

    def loaded_page_title(self):
        return self.browser.title

    def result_link_titles(self):
        result_links = self.browser.find_elements(By.CLASS_NAME, "react-results--main")
        return [link.text for link in result_links]