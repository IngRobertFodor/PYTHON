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


# Create a program that asks the user for a number and then prints out a list of all the divisors of that number.
# For example, 14 is a divisor of 28 because 28/14 has no remainder.

# Ask user for his number.
my_number = input("Give me some number: ")
print("Your number was " + my_number + ".")
my_number = int(my_number)

# Create group of possible divisors.
x = my_number + 1
x = int(x)
print(x)
numbers_division = range(1,x)
for y in numbers_division:
    print(y)

# We can create list of possible divisors, not just print them.
numbers_division_list = list(numbers_division)
print(numbers_division_list)

# Divisors.
result_list = []
for z in numbers_division_list:
    if my_number % z == 0:
        result_list.append(z)
    else:
        pass
print(result_list)