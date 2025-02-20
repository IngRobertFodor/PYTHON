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


try:
    with open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "rt") as f:
        print(f.read())
finally:
    f.close()
print()

# Read first 5 characters.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.read(5))
f.close()
print()

# Read first 2 lines.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.readline())
print(f.readline())
f.close()
print()

# Add text to the end of the file.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "a")
f.write("Now the file has more content!")
f.close()
# Open and read the file after the appending.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.read())
f.close()
print()

# Add text from the beginning of the file.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "w")
f.write("Now the file has more content!")
f.close()
# Open and read the file after.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.read())
f.close()

# Creates new file.
# f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\myfile.txt", "x")

# os.remove("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt")