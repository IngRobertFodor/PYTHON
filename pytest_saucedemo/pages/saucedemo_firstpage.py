from selenium.webdriver.common.by import By


class SauceDemo_FirstPage:

    def __init__(self, driver):
        self.driver = driver

    def load_page(self, url):
        self.driver.get(url)
    
    def login(self, username, password): 
        username_field = self.driver.find_element(By.ID, "user-name")
        password_field = self.driver.find_element(By.ID, "password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button = self.driver.find_element(By.ID, "login-button")
        login_button.click()

    def webshop_productspage_title(self):
        firstpage_title = self.driver.find_element(By.CLASS_NAME, "title").text
        return firstpage_title
    
    def webshop_lockedoutuser_error(self):
        error_message = self.driver.find_element(By.TAG_NAME, "h3").text
        return error_message