from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


driver = webdriver.Firefox()
driver.get("https://www.selenium.dev/")
time.sleep(2)
print()

title_relative_path = driver.find_element(By.XPATH, "//h1")
print("Find element by XPATH:",title_relative_path.text)

title_relative_path_two = driver.find_element(By.XPATH, "//h1[@class='d-1 fw-bold']")
print("Find element by XPATH:",title_relative_path_two.text)

title_relative_path_id = driver.find_element(By.TAG_NAME, "h1")
print("Find element by TAG_NAME:",title_relative_path_id.text)

selenium_icon = driver.find_element(By.CLASS_NAME, "navbar-logo")
print("Find element by CLASS_NAME:", selenium_icon.text)

selenium_ide_icon = driver.find_element(By.CLASS_NAME, "selenium-button-container")
print("Find element by CLASS_NAME:", selenium_ide_icon.text)

print()

exercise_element_by_id = driver.find_element(By.ID, "selenium_webdriver")
print("Find element by ID:", exercise_element_by_id)
print("Find element by ID:", exercise_element_by_id.text)

exercise_element_by_tag_name = driver.find_element(By.TAG_NAME, "button")
print("Find element by TAG NAME:", exercise_element_by_tag_name)

exercise_element_by_xpath = driver.find_element(By.XPATH, "//h1[@class='d-1 fw-bold']")
print("Find element by XPATH:", exercise_element_by_xpath.text)

exercise_element_by_class_name = driver.find_element(By.CLASS_NAME, "selenium-logo")
print("Find element by CLASS_NAME:", exercise_element_by_class_name)

driver.quit()