# WEB TA PURPOSES
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome()
driver.get("http://www.python.org")
assert "Python" in driver.title
assert "PPython" not in driver.title
my_element = driver.find_element(By.NAME, "q")
my_element.clear()
my_element.send_keys("pycon")
my_element.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
# Closes one tab.
#driver.close()
# Closes browser.
driver.quit()