from selenium import webdriver
from selenium.webdriver.common.by import By
import time
# Interaction with the elements.
from selenium.webdriver.common.keys import Keys
# DROPDOWNs
from selenium.webdriver.support.ui import Select
# DRAG AND DROPs
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Firefox()
driver.get("https://the-internet.herokuapp.com/drag_and_drop")
time.sleep(2)


# DRAG AND DROP element.
source_element = driver.find_element(By.XPATH, "//*[@id='column-a']")
destination_element = driver.find_element(By.XPATH, "//*[@id='column-b']")

actions = ActionChains(driver)
actions.drag_and_drop(source_element, destination_element).perform()
time.sleep(4)

source_element = driver.find_element(By.XPATH, "//*[@id='column-b']")
print("B:",source_element.text)


driver.quit()