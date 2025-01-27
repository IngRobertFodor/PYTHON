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
# MATH PURPOSES
import math
# SEARCH PURPOSES (RegEx)
import re
# DELETE, FILE HANDLING PURPOSES
import os
# MATPLOTLIB, VISUALIZATION PURPOSES
import matplotlib
# MYSQL PURPOSES
import mysql.connector


# Long way, without list comprehensions.
list_a = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
list_result = []
for a in list_a:
    if a % 2 == 0:
        list_result.append(a)
# These are even numbers.
print(list_result)


# List comprehensions.
list_a = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
list_result = [a for a in list_a if a % 2 == 0]
print(list_result)


# Other training examples.
test_two = [b for b in list_result if b > 36]
print(test_two)
test_three = [c for c in list_a if c % 5 == 0]
print(test_three)