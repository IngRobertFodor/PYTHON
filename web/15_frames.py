# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# TEXT PURPOSES
from selenium.webdriver.common.keys import Keys
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC
# SLEEP PURPOSES
import time
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select
# SLIDER PURPOSES
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")


    # 0.1  This clicks on  "Frames"  link on selected web page, when it loads.
    frames_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "Frames")                                           
    ))
    frames_link.click()
    

    # 1.1  This clicks on  "Nested Frames"  link on selected web page, when it loads.
    nested_frames_link = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//a[@href='/nested_frames']")                                           
    ))
    nested_frames_link.click()
    time.sleep(2)
    
    
    # 2.1  Go back to previous page.
    driver.back()


    # 3.1  This clicks on  "iFrame"  link on selected web page, when it loads.
    iframe_link = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//a[@href='/iframe']")                                           
    ))
    iframe_link.click()

    headert_text_check = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@id='content']/div/h3")
    ))
    print(headert_text_check.text)  
   

    # 3.2  This clicks on File on selected web page.
    click_file = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//button[@class='tox-mbtn tox-mbtn--select' and @tabindex=-1]")
    ))
    click_file.click()
    time.sleep(2)


    # 3.3  This clicks on New document on selected web page.
    click_newdocument = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//div[@class='tox-collection__item-icon']")
    )).click()
    time.sleep(2)


    # 3.4  This will add my text there.
    driver.switch_to.frame("mce_0_ifr")
    driver.find_element(By.ID, "tinymce").send_keys("My Text!")
    time.sleep(2)
    

    # 3.5  This will check my text there.
    check_text = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//body[@id='tinymce']/p")
    ))
    print("My text is: ",check_text.text,".")


finally:
    driver.quit()