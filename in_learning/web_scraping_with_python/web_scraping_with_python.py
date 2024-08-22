from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager # type: ignore


def get_my_texts(url, xpath):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get(url)
    sleep(5)
    my_text = driver.find_element(By.XPATH, xpath)
    return my_text.text
    driver.quit()


url = "https://pythonscraping.com/linkedin/ietf.html"
xpath_text = "/html/body/div/pre/div/span[1]"
xpath_text_name = "/html/body/div/pre/span[1]"

def collect_texts(dict_name):
    dict_name = {
    "text":get_my_texts(url, xpath_text),
    "name":get_my_texts(url, xpath_text_name)
    }
    return dict_name

print(collect_texts("my_dict"))