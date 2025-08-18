from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


try:
    driver = webdriver.Firefox()
    driver.get("https://the-internet.herokuapp.com/")
    file_upload = driver.find_element(By.LINK_TEXT, "File Upload")
    file_upload.click()
    choose_file = driver.find_element(By.ID, "file-upload")
    choose_file.send_keys("C:\\Users\\I070494\\Downloads\\Testing Pyramid.png")
    driver.implicitly_wait(10)
    upload_button = driver.find_element(By.ID, "file-submit")
    upload_button.click()
    next_page = driver.find_element(By.TAG_NAME, "h3")
    assert next_page.text == "File Uploaded!"

finally:
    driver.quit()