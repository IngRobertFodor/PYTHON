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


# Write a program that takes a list of numbers and makes a new list of only the first and last elements of the given list.
a = [5, 10, 15, 20, 25]

def my_new_function():
    new_list = list()
    print(new_list)
    new_list.insert(0, a[-1])
    new_list.insert(0, a[0])
    print(new_list)

    if new_list == [5, 25]:
        print("Job done.")
    else:
        print(":-)")

    return

my_new_function()