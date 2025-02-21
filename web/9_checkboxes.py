# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Firefox()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Checkboxes"  link on selected web page, when it loads.
    checkboxes_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Checkboxes")))
    checkboxes_link.click()


    # 1.1  This do things with first checkbox on webpage.
    checkbox_one = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div div div input[type=checkbox]")))

    # Check status: Unchecked
    print(checkbox_one.is_selected())
    
    # This "Checks" the checkbox.
    checkbox_one.click()
    
    # Check status: Checked (type 1)
    print(checkbox_one.is_selected())
    # Check status: Checked (type 2)
    print("Checkbox 1 is now Checked:", checkbox_one.get_attribute("checked"), ".")


    # 1.2  This do things with second checkbox on webpage.
    checkbox_two = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@type='checkbox' and @checked]")))

    # Check status: Checked
    print(checkbox_two.is_selected())

    # This "Unchecks" the checkbox.
    checkbox_two.click()

    # Check status: Unchecked
    print(checkbox_two.is_selected())
    print("Checkbox 2 is now Checked:", checkbox_two.is_selected(), ", this means that it is Unchecked.")

finally:
    driver.quit()