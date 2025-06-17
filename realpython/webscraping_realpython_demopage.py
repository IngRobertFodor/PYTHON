import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.by import By


url = "https://realpython.github.io/fake-jobs/"
webpage_html_content = requests.get(url)
print(webpage_html_content.status_code)
print(webpage_html_content.text[0:45])
print()


url_theinternet = "https://the-internet.herokuapp.com/"
webpage_html_content = requests.get(url_theinternet)
print(webpage_html_content.status_code)
print(webpage_html_content.text[0:45])
print()


responce = requests.get("https://the-internet.herokuapp.com/basic_auth", auth=HTTPBasicAuth("admin", "admin"))
print(responce.status_code)
print(responce.text[0:5000])