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


    # 0.1  This clicks on  "Dynamic Loading"  link on selected web page, when it loads.
    dynamic_loading_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Dynamic Loading")))
    dynamic_loading_link.click()


    # 1.1  This clicks on  "Example 2: Element rendered after the fact"  link on selected web page, when it loads.
    example2_link = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@href='/dynamic_loading/2']")))
    example2_link.click()


    # 1.2  This checks 2 displayed texts.    
    displayed_text_one = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='example']/h3")))
    displayed_text_two = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='example']/h4")))
    print(displayed_text_one.text)
    print(displayed_text_two.text)


    # 1.3  This clicks on  "Start"  button.
    start_button= wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='start']/button")))
    start_button.click()
    
    
    # 1.4  This checks <h4> text.
    displayed_text_four = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='finish' and @style='']/h4")))
    print(displayed_text_four)
    my_text = displayed_text_four[0].text
    print(my_text)

finally:
    driver.quit()