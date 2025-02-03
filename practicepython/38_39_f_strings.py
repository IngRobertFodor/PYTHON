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
from matplotlib import pyplot as plt
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
# COLLECTIONS PURPOSES
import collections
# JSON PURPOSES (WORKING WITH FILES)
import json


name = input("Give me Your name: ")
print(f"Your name is {name}.")

age = input("How old are you? ")
age = str(age)
print(f"You are {age} years old.")

age = int(age)
diff_age = 100 - age
diff_age = str(diff_age)
print(f"You will turn 100 in {diff_age} years.")


print("OPTION 1 to write: \"You will be\".")
year_test_one = 2023 - age + 100
year_test_one = str(year_test_one)
print(f"You will be 100 years old in {year_test_one}.")

print("OPTION 2 to write: \"You will be\".")
current_date_time = datetime.datetime.now()
actual_date = current_date_time.date()
#actual_year = actual_date.strftime("%Y")
actual_year = datetime.datetime.now().year
print(f"Actual year is {actual_year}.")
actual_year = int(actual_year)
year_test_two = actual_year - age  + 100
year_test_two = str(year_test_two)
print(f"You will be 100 years old in {year_test_two}.")