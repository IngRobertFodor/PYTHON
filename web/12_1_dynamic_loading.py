# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Dynamic Loading"  link on selected web page, when it loads.
    dynamic_loading_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Dynamic Loading")                                           
    ))
    dynamic_loading_link.click()


    # 1.1  This clicks on  "Example 1: Element on page that is hidden"  link on selected web page, when it loads.
    example1_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Example 1: Element on page that is hidden")                                           
    ))
    example1_link.click()


    # 1.2  This checks 2 displayed texts.    
    displayed_text_one = wait.until(EC.presence_of_element_located(
        (By.TAG_NAME, "h3")
        ))
    
    displayed_text_two = wait.until(EC.presence_of_element_located(
        (By.TAG_NAME, "h4")
        ))
    print(displayed_text_one.text)
    print(displayed_text_two.text)

    
    # 1.3  This checks hidden <h4> text.
    displayed_text_three = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[@id='finish' and @style='display:none']/h4")
        ))
    print(displayed_text_three)

    
    # 1.4  This clicks on  "Start"  button.
    start_button= wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@id='start']/button")                                          
    ))
    start_button.click()
    
    
    # 1.5  This checks <h4> text.
    displayed_text_four = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//div[@id='finish' and @style='']/h4")
        ))
    print(displayed_text_four)
    

finally:
    driver.quit()