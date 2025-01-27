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


# Write a program that returns a list, that contains no duplicates.

# Use "+" method to join two lists.
a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
joined_list = a + b
print(joined_list)
# Convert list to set, because set can not have duplicates.
converted_list_to_set = set(joined_list)
print(converted_list_to_set)


# Randomly generate two lists to test joining lists without duplicates.

# Use "import random" module (already imported above).
c_one = random.randrange(5,15)
print(c_one)
d_one = random.randrange(16,20)
print(d_one)
e_one = list(range(c_one,d_one))
print(e_one)
c_two = random.randrange(5,15)
print(c_two)
d_two = random.randrange(16,20)
print(d_two)
e_two = list(range(c_two,d_two))
print(e_two)
e_one_and_two = set(e_one + e_two)
print(e_one_and_two)