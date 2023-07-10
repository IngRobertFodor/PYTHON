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


# Path should start like this: "C:\\".
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "rt")
print(f.read())


# Read first 5 characters.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.read(5))


# Read first 2 lines.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.readline())
print(f.readline())


# Loop through the file line by line.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
for x in f:
  print(x)


#
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.readline())
f.close()


# Add text to the end of the file.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "a")
f.write("Now the file has more content!")
f.close()
# Open and read the file after the appending.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.read())
# Result: Now the file has more content!Now the file has more content!.


# Add text from the beginning of the file.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "w")
f.write("Now the file has more content!")
f.close()
# Open and read the file after.
f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt", "r")
print(f.read())
# Result: Now the file has more content!.


# Creates my new file.
# f = open("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\myfile.txt", "x")


# os.remove("C:\\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\w3schools\TestFile.txt")