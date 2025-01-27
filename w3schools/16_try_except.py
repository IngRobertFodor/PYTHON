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


# 1
try:
  print(x)
except:
  print("An exception occurred")
# Result: An exception occurred.

# 2.
try:
  print(x)
except NameError:
  print("Variable x is not defined")
except:
  print("Something else went wrong")
# Result: Variable x is not defined.

# 3
# The try block does not raise any errors, so the else block is executed.
try:
  print("Hello")
except:
  print("Something went wrong")
else:
  print("Nothing went wrong")
# Result: Hello Nothing went wrong.

# 4
# The finally block gets executed no matter if the try block raises any errors or not.
try:
  print(x)
except:
  print("Something went wrong")
finally:
  print("The 'try except' is finished")
# Result: Something went wrong The 'try except' is finished.

# 5
x = -1
if x < 0:
  raise Exception("Sorry, no numbers below zero")
# Result: Exception: Sorry, no numbers below zero.

'''
# 6
x = "hello"
if not type(x) is int:
  raise TypeError("Only integers are allowed")
# Result: TypeError: Only integers are allowed.
'''