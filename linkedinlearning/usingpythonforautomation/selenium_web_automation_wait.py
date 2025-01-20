from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
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
text = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="input-example"]/p')))
print(text.text)
print()

button_remove = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkbox-example"]/button')))
button_remove.click()
text = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="checkbox-example"]/p')))
print(text.text)
print()

button_add = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkbox-example"]/button')))
button_add.click()
text = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="checkbox-example"]/p')))
print(text.text)
print()

checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkbox"]')))
checkbox.click()
print("Checkbox checked:", checkbox.is_selected())

driver.quit()