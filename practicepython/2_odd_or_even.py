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
# SEARCH PURPOSES (RegEx)
import re
# DELETE, FILE HANDLING PURPOSES
import os
# MATPLOTLIB, VISUALIZATION PURPOSES
import matplotlib


# Ask the user for a "number" and "number to divide with".
number = input("Give me some number: ")
print("Your number was " + number + ".")
number = int(number)
number_to_divide_with = input("Give me some number to divide: ")
print("Your number to divide was " + number_to_divide_with + ".")
number_to_divide_with = int(number_to_divide_with)


# Check wheteher "number" and "number_to_divide_with" are divided evenly.
number = int(number)
divide_evenly = number % number_to_divide_with
if divide_evenly == 0:
    print("Divided evenly.")
    print(number / number_to_divide_with)
else:
    print("Not divided evenly.")
    print(number / number_to_divide_with)


# "% 5" means that users´s number can be divided by 5 with 0 waste.
result = number % 5
result = int(result)
if result == 0:
    print("Your number can be divided by 5.")
else:
    print("This is not the simple division.")


# Check if number is a multiple of 4.
test_of_division_by_four = number % 4
if test_of_division_by_four == 0:
    print("Your number can be divided by 4.")
else:
    print("Your number can not be divided by 4.")


# Check whether the number is even or odd.
test_even_odd_number = number % 2
if test_even_odd_number == 0:
    number = str(number)
    print("The number " + number + " is even.")
else:
    number = str(number)
    print("The number " + number + " is odd.")