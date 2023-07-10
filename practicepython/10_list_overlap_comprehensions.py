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


# Part1: 
a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

print(a, b)
# Without List Comprehension for Part1
c = a + b
print(c)
c = set(c)
print(c)

# With List Comprehension for Part1
for x in b: a.append(x)
print(set(a))


# Part2:
num_one_range_one = random.randrange(1,11)
num_two_range_one = random.randrange(11,21)
print(num_one_range_one,num_two_range_one)
range_one = list(range(num_one_range_one,num_two_range_one))
print(range_one)

num_one_range_two = random.randrange(5,21)
num_two_range_two = random.randrange(21,31)
print(num_one_range_two,num_two_range_two)
range_two = list(range(num_one_range_two,num_two_range_two))
print(range_two)


# List Comprehension for Part2
for x in range_two: range_one.append(x)
print(set(range_one))