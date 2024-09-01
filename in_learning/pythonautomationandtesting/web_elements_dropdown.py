from selenium import webdriver
import time
from selenium.webdriver.common.by import By
# Interaction with the elements.
from selenium.webdriver.common.keys import Keys
# DROPDOWNs
from selenium.webdriver.support.ui import Select
# DRAG AND DROPs
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Firefox()
driver.get("https://wiki.python.org/moin/BeginnersGuide")
time.sleep(2)


# DROPDOWN element.

dropdown = Select(driver.find_element(By.XPATH, "//*[@id='sidebar']/div[3]/ul/li[5]/form/div/select"))
time.sleep(2)
dropdown.select_by_visible_text("Raw Text")
time.sleep(2)
# Switch back to the first tab
driver.back()
time.sleep(2)

dropdown.select_by_index(2)
time.sleep(2)
# Switch back to the first tab
driver.back()
time.sleep(2)

dropdown.select_by_value("raw")
time.sleep(2)
# Switch back to the first tab
driver.back()
time.sleep(2)


# BUTTON element.

login = driver.find_element(By.XPATH, "//*[@id='login']")
login.click()
time.sleep(2)  
button = driver.find_element(By.XPATH, "//*[@id='loginform']/div/table/tbody/tr[5]/td[2]/input[2]")
button.click()
time.sleep(2)
text = driver.find_element(By.ID, "Learning_Python")
print("This is the text:", text.text)


driver.quit()