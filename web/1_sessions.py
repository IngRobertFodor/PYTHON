from selenium import webdriver

# webdriver.Firefox()
# webdriver.Chrome()
# webdriver.Safari()
# webdriver.Edge()

driver = webdriver.Firefox(
    firefox_binary="C:\\Program Files\\Mozilla Firefox\\firefox.exe"
)

try:
    driver.get("http://www.google.com")
    driver.get("http://www.gmail.com")

finally:
        driver.quit()

# webdriver.Remote()
