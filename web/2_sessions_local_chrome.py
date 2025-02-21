from selenium import webdriver
from selenium.webdriver.firefox.options import Options


options = Options()
options.page_load_strategy = 'normal'

driver = webdriver.Firefox(options=options)

driver.get("http://www.google.com")
driver.get("http://www.gmail.com")

driver.quit()