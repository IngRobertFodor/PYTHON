from selenium.webdriver.common.by import By


class Web_Result:

    def __init__(self, browser):
        self.browser = browser

    def check_web_url(self):
        return self.browser.current_url
    
    def web_text(self):
        text = self.browser.find_element(By.TAG_NAME, "h1").text
        return text