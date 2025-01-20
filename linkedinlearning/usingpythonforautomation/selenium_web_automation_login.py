from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from time import sleep


url = "https://the-internet.herokuapp.com/login"

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.maximize_window()

driver.get(url)
sleep(5)

# Find username and password fields and fill them out.
username = driver.find_element(By.XPATH, '//*[@id="username"]')
username.send_keys("tomsmith")
sleep(2)
password = driver.find_element(By.NAME, 'password')
password.send_keys("SuperSecretPassword!")
sleep(2)
# Find and click the login button.
button_login = driver.find_element(By.TAG_NAME, 'button')
button_login.click()
check_login = driver.find_element(By.ID, 'flash')
my_text = driver.find_element(By.TAG_NAME, 'h4')
# This is Compare.
try:
	print(check_login.text)
	print(my_text.text)
except:
	print("Login Failed.")

driver.quit()