import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from selenium.webdriver.common.action_chains import ActionChains
# IMPLICIT WAIT
from time import sleep
# EXPLICIT WAIT
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = "https://the-internet.herokuapp.com/dynamic_controls"

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.maximize_window()

driver.get(url)
# IMPLICIT WAIT
sleep(5)

# EXPLICIT WAIT
button_enable = driver.find_element(By.XPATH, '//*[@id="input-example"]/button')
button_enable.click()
wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="message"]')))
text = driver.find_element(By.XPATH, '//*[@id="message"]')
# Text Compare.
print(text.text)

driver.quit()