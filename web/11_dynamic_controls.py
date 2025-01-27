# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select


driver = webdriver.Chrome()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Dynamic Controls"  link on selected web page, when it loads.
    dynamic_controls_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Dynamic Controls")                                           
    ))
    dynamic_controls_link.click()


    # 1.1  This do things with checkbox (A checkbox) on webpage.
    checkbox_one = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@type='checkbox' and @label='blah']")                                          
    ))

    # Check status (A checkbox): Unchecked
    print(checkbox_one.is_selected())
    # This "Checks" the checkbox.
    checkbox_one.click()
    # Check status (A checkbox): Checked
    print(checkbox_one.is_selected())
    # This "Unchecks" the checkbox.
    checkbox_one.click()
    # Check status (A checkbox): Unchecked
    print(checkbox_one.is_selected())


    # 1.2  This clicks on button (Remove). It removes checkbox.
    remove_button = wait.until(EC.presence_of_element_located(
               (By.XPATH, "//button[@type='button' and @onclick='swapCheckbox()']")                                    
    ))
    remove_button.click()
    

    # 1.3  This clicks on button (Add). It will add checkbox.
    add_button = wait.until(EC.presence_of_element_located(
               (By.XPATH, "//button[@type='button' and @onclick='swapCheckbox()']")                                    
    ))
    add_button.click()


    # 1.4  This shows URL of the web page.
    print(driver.current_url)


    # 1.5  This do things with checkbox (A checkbox) on webpage.
    checkbox_one = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@type='checkbox' and @label='blah']")                                          
    ))

    # Check status (A checkbox): Unchecked
    print(checkbox_one.is_selected())
    # This "Checks" the checkbox.
    checkbox_one.click()
    # Check status (A checkbox): Checked
    print(checkbox_one.is_selected())


finally:
    driver.quit()