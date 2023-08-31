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
# SLIDER PURPOSES - IN THIS SCRIPT
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
# COLLECTIONS PURPOSES
import collections
# JSON PURPOSES (WORKING WITH FILES)
import json


# This will read from .json file "birthday_json_two.json".
with open("birthday_json_two.json", "r") as open_file:
    data = json.load(open_file)

print(data.values())
c = []
for i in (data.values()):
    a = (i[0:2])
    print(a)
    if a == "01":
        a = "January"
    elif a == "02":
        a = "February"
    elif a == "03":
        a = "March"
    elif a == "04":
        a = "April"
    elif a == "05":
        a = "May"
    elif a == "06":
        a = "June"
    elif a == "07":
        a = "July"
    elif a == "08":
        a = "August"
    elif a == "09":
        a = "September"
    elif a == "10":
        a = "October"
    elif a == "11":
        a = "November"
    elif a == "12":
        a = "December"
    c.append(a)

print(c)
print(collections.Counter(c))