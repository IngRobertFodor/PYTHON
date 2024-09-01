from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


driver = webdriver.Firefox()
driver.get("https://python.org/")
time.sleep(2)

element_by_id = driver.find_element(By.ID, "submit")
print("Find element by ID:", element_by_id)
time.sleep(2)
element_by_name = driver.find_element(By.NAME, "submit")
print("Find element by NAME:", element_by_name)
time.sleep(2)
python_logo = driver.find_element(By.CLASS_NAME, "python-logo")
print("Find element by CLASS NAME:", python_logo)
time.sleep(2)
python_logo_xpath = driver.find_element(By.XPATH, "//*[@id='touchnav-wrapper']/header/div/h1/a/img")
print("Find element by XPATH:", python_logo_xpath)
python_logo_xpath_two = driver.find_element(By.XPATH, "//img[@class='python-logo']")
print("Find element by XPATH:", python_logo_xpath_two)
time.sleep(2)

search_field = driver.find_element(By.ID, "id-search-field")
print("Find element by ID:", search_field)
time.sleep(2)
search_field.clear()
search_field.send_keys("python automation")
search_field.send_keys(Keys.RETURN)
time.sleep(2)

driver.quit()