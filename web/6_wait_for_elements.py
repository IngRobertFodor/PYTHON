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
    # WAIT PURPOSES
    # It converts this:
    # driver.find_element(By.LINK_TEXT, "Form Authentication")
    # for wait purposes.
    wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Form Authentication")                                           
    ))
    # To check what actual url is, before "EC.url_to_be" check.
    print(driver.current_url)
    wait.until(EC.url_to_be("https://the-internet.herokuapp.com/"))

finally:
    driver.quit()