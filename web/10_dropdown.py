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


driver = webdriver.Firefox()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Dropdown"  link on selected web page, when it loads.
    dropdown_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Dropdown")))
    dropdown_link.click()


    # 1.1  This do things with dropdown on webpage.
    dropdown = Select(driver.find_element(By.ID, "dropdown"))
    

    # 1.2  Setting ASSERTION
    # ASSERTION checks whether expected value is selected.
    option_two = driver.find_element(By.CSS_SELECTOR, "option[value='2']")

    # 1.3.1  OK
    dropdown.select_by_index(2)
    assert option_two.is_selected()
    
    # 1.3.2  ASSERTION ERROR
    dropdown.select_by_visible_text("Option 2")
    assert option_two.is_selected()

finally:
    driver.quit()