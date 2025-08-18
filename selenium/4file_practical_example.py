from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


try:
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 10)

    webpage_url = "https://www.selenium.dev/documentation/webdriver/getting_started/"
    driver.get(webpage_url)
    current_webpage_title = driver.find_element(By.TAG_NAME, "h1")
    #print(current_webpage_title.text)
    assert "Getting started" in current_webpage_title.text
    assert "Getting Started" not in current_webpage_title.text

    driver.get("https://www.selenium.dev/documentation/webdriver/getting_started/first_script/")
    python_button = wait.until(EC.element_to_be_clickable((By.ID, "tabs-02-01-tab")))
    python_button.click()
    python_code = driver.find_elements(By.TAG_NAME, "code")
    for code in python_code:
        if code.text=="title = driver.title":
             #print(code.text)
             assert "title = driver.title" in code.text

finally:
    driver.quit()