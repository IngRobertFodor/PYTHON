import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


url = "https://the-internet.herokuapp.com/drag_and_drop"

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.maximize_window()

driver.get(url)
sleep(5)

draganddrop_url = driver.current_url
print("This is our web address:",draganddrop_url)
print("This is our web title:",driver.title)
print()

source = driver.find_element(By.XPATH, '//*[@id="column-a"]')
destination = driver.find_element(By.XPATH, '//*[@id="column-b"]')

actions = ActionChains(driver)
actions.drag_and_drop(source, destination).perform()
sleep(5)

driver.quit()