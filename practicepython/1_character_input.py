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


# What happens at the end of input() is that it waits for the user to type something and press ENTER. Only after the user presses ENTER the program will continue.
name = input("Give me Your name: ")
print("Your name is " + name + ".")

# If you know, that user will type number, where only string passes, you can switch integer to string using str() function. In opposite cases you can use int() function as well.
age = input("How old are you? ")
age = str(age)
print("You are " + age + " years old.")

age = int(age)
diff_age = 100 - age
diff_age = str(diff_age)
print("You will turn 100 in " + diff_age + " years.") 

print("OPTION 1 to write: \"You will be \".")
year_test_one = 2023 - age + 100
year_test_one = str(year_test_one)
print("You will be 100 years old in " + year_test_one + ".")

print("OPTION 2 to write: \"You will be \".")
current_date_time = datetime.datetime.now()
actual_date = current_date_time.date()
actual_year = actual_date.strftime("%Y")
actual_year = int(actual_year)
year_test_two = actual_year - age  + 100
year_test_two = str(year_test_two)
print("You will be 100 years old in " + year_test_two + ".")

phone_num = input("Give me your phone num please: ")
print("Your phone number is: " + str(phone_num) + ".")


print(5 * "test", end="\n")

xxxx = [5 * "test_x"]
for x in xxxx:
  print(x, end="")

yyyy = [5 * "test_y"]
for y in yyyy:
  print(y, end="\n")

print("Hello", end="")
print("World")