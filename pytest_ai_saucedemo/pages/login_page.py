from selenium.webdriver.common.by import By


class LoginPage:
    
    # 1. Constructor: Initializes the driver
    def __init__(self, driver):
        self.driver = driver
    
    # 2. Actions (Methods): Defining the functions the page can perform    
    def enter_credentials(self, username, password):
        #Enters the provided username and password into the fields.
        self.driver.find_element(By.ID, "user-name").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        
    def click_login(self):
        #Clicks the login button.
        self.driver.find_element(By.ID, "login-button").click()
        
    def login(self, username, password):
        #Combines credential entry and clicking login.
        self.enter_credentials(username, password)
        self.click_login()