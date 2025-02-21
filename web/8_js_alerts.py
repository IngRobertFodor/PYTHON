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
    
    # MINIMIZE, MAXIMIZE WINDOW
    driver.minimize_window()
    driver.maximize_window()


    # 0.1  This clicks on  "JavaScript Alerts"  link on selected web page, when it loads.
    js_alert_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "JavaScript Alerts")))
    js_alert_link.click()


    # 1.1  This clicks on  "Click for JS Alert"  button.
    alert_first_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div div div ul li button")))
    alert_first_button.click()
    
    alert = driver.switch_to.alert
    text = alert.text
    print(text)
    alert.accept()

    # 1.2  This shows result text on web page.
    result_first_text = wait.until(EC.presence_of_element_located((By.ID, "result")))
    print(result_first_text.text) 


    # 2.1  This clicks on  "Click for JS Confirm"  button.
    alert_second_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div div div ul li:nth-child(2) button")))
    alert_second_button.click()
    
    alert = driver.switch_to.alert
    secondtext = alert.text
    print(secondtext)
    alert.dismiss()

    # 2.2  This shows result text on web page.
    result_second_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#result")))
    print(result_second_text.text) 


    # 3.1  This clicks on  "Click for JS Prompt"  button.
    alert_third_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div div div ul li:nth-child(3) button")))
    alert_third_button.click()
    
    alert = driver.switch_to.alert
    thirdtext = alert.text
    print(thirdtext)
    alert.send_keys("Test of inserting text to alert.")
    alert.accept()

    # 3.2  This shows result text on web page.
    result_third_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#result")))
    print(result_third_text.text) 

finally:
    driver.quit()