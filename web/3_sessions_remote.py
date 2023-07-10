"""
!!!

It is necessary to run this:
    geckodriver
in second CMD Terminal.

And then back in the first CMD Terminal to run:
    python sessions_remote.py

!!!
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.page_load_strategy = 'normal'
options.binary_location = r"C:\\Program Files\\Mozilla Firefox\\firefox.exe"

driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4444",
    options=options
)

driver.get("http://google.com")
driver.get("http://www.gmail.com")

driver.quit()