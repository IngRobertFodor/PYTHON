from selenium import webdriver
import time
from selenium.webdriver.common.by import By


driver = webdriver.Firefox()
driver.get("https://www.selenium.dev/")
print("Page Title: ", driver.title)
time.sleep(2)

title_relative_xpath = driver.find_element(By.XPATH, "//h1")
print("Find element by XPATH:",title_relative_xpath.text)

title_relative_xpath_two = driver.find_element(By.XPATH, "//h1[@class='d-1 fw-bold']")
print("Find element by XPATH:",title_relative_xpath_two.text)

title_relative_xpath_three = driver.find_element(By.XPATH, "/html/body/div/main/section[1]/div/div/div/h1")
print("Find element by XPATH:",title_relative_xpath_three.text)

title_relative_path_tag_name = driver.find_element(By.TAG_NAME, "h1")
print("Find element by TAG_NAME:",title_relative_path_tag_name.text)

selenium_icon = driver.find_element(By.CLASS_NAME, "navbar-logo")
print("Find element by CLASS_NAME:", selenium_icon.text)

selenium_ide_icon = driver.find_element(By.ID, "selenium_ide")
print("Find element by ID:", selenium_ide_icon.text)

text_relative_xpath = driver.find_element(By.XPATH, "//p[@class='lead mt-3 mb-0']")
print("Find element by XPATH:",text_relative_xpath.text)

driver.get("https://www.selenium.dev/documentation/about/")
time.sleep(2)
driver.back()
time.sleep(2)
driver.forward()
time.sleep(2)
driver.refresh()

driver.quit()