# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# TEXT PURPOSES
from selenium.webdriver.common.keys import Keys
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC
# SLEEP PURPOSES
import time
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select
# SLIDER PURPOSES
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Firefox()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Frames"  link on selected web page, when it loads.
    frames_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Frames")))
    frames_link.click()
    

    # 1.1  This clicks on  "Nested Frames"  link on selected web page, when it loads.
    nested_frames_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/nested_frames']")))
    nested_frames_link.click()
    time.sleep(2)
    
    
    # 2.1  Go back to previous page.
    driver.back()


    # 3.1  This clicks on  "iFrame"  link on selected web page, when it loads.
    iframe_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/iframe']")))
    iframe_link.click()

    headert_text_check = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='content']/div/h3")))
    print(headert_text_check.text)

finally:
    driver.quit()