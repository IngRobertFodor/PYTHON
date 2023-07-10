from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.page_load_strategy = 'normal'

driver = webdriver.Chrome(options=options)
try:
    driver.get("http://www.google.com")
    driver.get("http://www.gmail.com")

finally:
    driver.quit()