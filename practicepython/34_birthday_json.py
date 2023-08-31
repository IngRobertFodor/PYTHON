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




# 1.1 Exercise
# This will create .json file "birthday_json_one.json" with dictionary "info_about_me" there.

info_about_me = {
    "name": "Michele",
    "has_a_dog": False
}
'''
# This will create .json file "birthday_json_one.json".
with open("birthday_json_one.json", "w") as open_file:
    json.dump(info_about_me, open_file)
'''
# This will read from .json file "birthday_json_one.json".
with open("birthday_json_one.json", "r") as open_file:
    info = json.load(open_file)

print("Does Michelle has a dog?: " + str(info["has_a_dog"]) + ".")




# 2.1 Exercise
# This will create .json file "birthday_json_two.json" with dictionary "birthdays_dictionary" there.  

birthdays_dictionary = {
    "Albert Einstein": "03/14/1879",
    "Benjamin Franklin": "01/17/1706",
    "Ada Lovelace": "12/10/1815",
    "Donald Trump": "06/14/1946",
    "Rowan Atkinson": "01/6/1955"
}
'''
# This will create .json file "birthday_json_two.json".
with open("birthday_json_two.json", "w") as open_file:
    json.dump(birthdays_dictionary, open_file)
'''
# This will read from .json file "birthday_json_two.json".
with open("birthday_json_two.json", "r") as open_file:
    data = json.load(open_file)

print("Einstein's birthday: " + str(data["Albert Einstein"]) + ".")