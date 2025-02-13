# WEB TA PURPOSES
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# IMPLICIT WAIT PURPOSES
import time
# EXPLICIT WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC


# You can find below element
    # <input type="text" name="passwd" id="passwd-id" />
# using these:
    # element = driver.find_element(By.ID, "passwd-id")
    # element = driver.find_element(By.NAME, "passwd")
    # element = driver.find_element(By.XPATH, "//input[@id='passwd-id']")
    # element = driver.find_element(By.CSS_SELECTOR, "input#passwd-id")


#driver = webdriver.Chrome()
driver = webdriver.Firefox()

try:    
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")    
    # To check what actual url is, "EC.url_to_be" check.
    wait.until(EC.url_to_be("https://the-internet.herokuapp.com/"))
    print(driver.current_url)

    # WAIT PURPOSES
    # It converts this:
    # driver.find_element(By.LINK_TEXT, "Form Authentication")

    # 1.Example
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Form Authentication")))
    print(driver.find_element(By.LINK_TEXT, "Form Authentication").is_displayed())
    print("Should be: Form Authentication:", driver.find_element(By.LINK_TEXT, "Form Authentication").text)
    
    # 2.Example
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Geolocation")))
    print(driver.find_element(By.LINK_TEXT, "Geolocation").is_displayed())
    print("Should be: Geolocation:",driver.find_element(By.LINK_TEXT, "Geolocation").text)
    driver.find_element(By.LINK_TEXT, "Geolocation").click()
    print(driver.find_element(By.TAG_NAME, "button").is_displayed())
    print("Should be: Where am i?:", driver.find_element(By.TAG_NAME, "button").text)  

finally:

    # Closes one tab.
    #driver.close()
    # Closes browser.
    driver.quit()