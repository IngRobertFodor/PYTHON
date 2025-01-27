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
# SLIDER PURPOSES
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Horizontal Slider"  link on selected web page, when it loads.
    horizontal_slider_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Horizontal Slider")                                           
    ))
    horizontal_slider_link.click()
    

    # 1.1  This checks header text on opened page.
    check_header_text = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@class='example']/h3")                                           
    ))
    print(check_header_text.text)


    # 1.2  Move slider to position 4 of 5.
    slider = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@type='range']")                                           
    ))
    move = ActionChains(driver)
    move.click_and_hold(slider).move_by_offset(40.0 , 0).release().perform()
   

    # 1.3  This checks slider value.
    slider_check_value = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//span[@id='range']")                                           
    ))
    print(slider_check_value.text)


    # 1.4  Move slider to position 2 of 5.
    slider = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@type='range']")                                           
    ))
    move = ActionChains(driver)
    move.click_and_hold(slider).move_by_offset(-15.0 , 0).release().perform()
   

    # 1.5  This checks slider value.
    slider_check_value = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//span[@id='range']")                                           
    ))
    print(slider_check_value.text)


finally:
    driver.quit()