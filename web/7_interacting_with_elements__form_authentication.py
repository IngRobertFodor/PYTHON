# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")
    
    # This clicks on  "Form Authentication"  link on selected web page, when it loads.
    form_auth_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Form Authentication")                                           
    ))
    form_auth_link.click()
    
    # This fills in username.
    username = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#username")                                          
    ))
    username.send_keys("tomsmith")

    # This fills in password.
    password = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#password")                                          
    ))
    password.send_keys("SuperSecretPassword!")

    # This clicks on Login button.
    login_button = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "button[type=submit]")                                          
    ))
    login_button.click()
    # Same - click Login button differently:
    # login_button = driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
    # login_button.click()

    # This clicks on Logout.
    logoutfrompage = wait.until(EC.presence_of_element_located(
               (By.LINK_TEXT, "Logout")
    ))
    logoutfrompage.click()

    # This is about message shown.
    flash = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#flash")
    ))
    assert "logged out" in flash.text

finally:
    driver.quit()