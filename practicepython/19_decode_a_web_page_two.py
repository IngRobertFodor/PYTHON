# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# FINDING ELEMENTS PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install htmldom==2.0
from htmldom import htmldom
# TEXT PURPOSES
from selenium.webdriver.common.keys import Keys
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC
# SLEEP PURPOSES
import time
# DATE TIME PURPOSES
import datetime
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select
# SLIDER PURPOSES
from selenium.webdriver.common.action_chains import ActionChains
# RANDOM PURPOSES
# https://www.w3schools.com/python/module_random.asp
# Import the random module, and display a random number between 1 and 9:
import random
# STRING PURPOSES
import string
# MATH PURPOSES
import math
# MATH PURPOSES - Fractions
import fractions
# SEARCH PURPOSES (RegEx)
import re
# DELETE, FILE HANDLING PURPOSES
import os
# MATPLOTLIB, VISUALIZATION PURPOSES
import matplotlib
# MYSQL PURPOSES
import mysql.connector
# REQUESTS PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install requests
import requests
# BEAUTIFUL SOUP PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install bs4
from bs4 import BeautifulSoup


driver = webdriver.Chrome()
try:
    # This is just test to open the browser.
    driver.get("https://www.nytimes.com")
    
    # These steps do things for this exercise.
    web_page_url = "https://www.vanityfair.com/style/society/2014/06/monica-lewinsky-humiliation-culture"
    web_page_displayed = requests.get(web_page_url)
    print(web_page_displayed.url)
    html = web_page_displayed.content
    soup = BeautifulSoup(html, features="html.parser")
    
    # This prints the web page text.
    for t in soup.find_all("div", class_ = "body__inner-container"):
        print(t.text)
    # Empty row.
    print()
    
    # This prints the first section of web page text.
    first_text = soup.find_all("div", class_ = "body__inner-container")
    print(first_text[0].text)
    # Empty row.
    print()
    
    # This 1. prints and then 2. saves the fourth section of web page text to the txt file.
    fourth_text = soup.find_all("div", class_ = "body__inner-container")
    # 1. print
    print(fourth_text[3].text)
    # 2. save
    with open("file_to_save_fourth_text.txt", "w") as open_file:
        open_file.write(fourth_text[3].text)

finally:
    # This is just test to close the browser.
    driver.quit()