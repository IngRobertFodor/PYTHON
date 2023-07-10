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
# MYSQL PURPOSES
import mysql.connector


# Excercise 1,2

# Make a new list that has all the elements less than 5 from list "a" and print out this new list.

# Option 1
xxx = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
bbb = [yyy for yyy in xxx if yyy<5]
print(xxx)
print(bbb)

# Option 2
a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
b = a[0:4]
print(a)
print(b)

# Option 3, but the result is not list.
x = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
for y in x:
    if y<5:
        print(y)
    else:
        pass


# Excercise 3

# Ask the user for a number and return a list that contains only elements from the original list a that are smaller than that number given by the user.

xxx = [1, 1, 2, 3, 5, 8, 14, 21, 34, 55, 89]

my_number = input("Give me some number: ")
print("Your number was " + my_number + ".")
my_number = int(my_number)

xxx.append(my_number)
print(xxx)
xxx.sort()
print(xxx)

bbb = [yyy for yyy in xxx if yyy<11]
print(bbb)