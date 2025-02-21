from selenium import webdriver


# webdriver.Firefox()
# webdriver.Chrome()
# webdriver.Safari()
# webdriver.Edge()

driver = webdriver.Firefox()

try:
    driver.get("http://www.google.com")
    driver.get("http://www.gmail.com")

finally:
        driver.quit()

# webdriver.Remote()