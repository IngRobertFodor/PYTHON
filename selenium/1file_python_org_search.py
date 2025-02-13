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


driver = webdriver.Firefox()

wait = WebDriverWait(driver, 10)

try:
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    assert "PPython" not in driver.title

    my_element = driver.find_element(By.NAME, "q")
    my_element.clear()
    time.sleep(4)
    my_element.send_keys("pycon")
    my_element.send_keys(Keys.ENTER)
    assert "No results found." not in driver.page_source
    button_text = driver.find_element(By.XPATH, "//*[@class='donate-button']")
    print(button_text.text)

finally:
    # Closes one tab.
    #driver.close()
    # Closes browser.
    driver.quit()