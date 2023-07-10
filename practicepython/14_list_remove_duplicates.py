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


# Convert list to set (to filter) and then back to list, using function.

# Option 1 - Using set().
list_a = [True, 11, "Test", "test", 5, (1, 2, 3), 11, "a", "a"]
print(len(list_a))
print(list_a)
list_b = [1, 1, 5]
print(len(list_b))
print(list_b)

def convert_list(x):
    set_x = set(x)
    print(len(set_x))
    print(set_x)
    list_x_updated = list(set_x)
    print(len(list_x_updated))
    return print(list_x_updated)

print("Option 1: Function \"convert_list\" results.")
convert_list(list_a)
convert_list(list_b)
# Empty row.
print()

# Option 2 - Using loop.
list_c = []

def function_with_loop():
    a = random.randrange(1,11)
    print(a)
    b = random.randrange(11,21)
    print(b)
    c = range(a,b)
    for cc in c:
        list_c.append(cc)
    return print(list_c)

print("Option 2: Function \"function_with_loop\" results.")
function_with_loop()
# Empty row.
print()

# Option 3 - Using Exercise 5.
list_d = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
list_e = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

def joined_list_function(x, y):
    # Use "+" method to join two lists.
    joined_list = x + y
    print(joined_list)
    # Convert list to set, because set can not have duplicates.
    converted_list_to_set = set(joined_list)
    print(converted_list_to_set)
    # Convert set to list.
    converted_set_to_list = list(converted_list_to_set)
    return print(converted_set_to_list)

print("Option 3 - Using Exercise 5.")
joined_list_function(list_d, list_e)
joined_list_function(list_a, list_b)