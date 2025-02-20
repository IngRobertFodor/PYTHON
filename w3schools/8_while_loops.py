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
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select
# SLIDER PURPOSES
from selenium.webdriver.common.action_chains import ActionChains
# RANDOM PURPOSES
# https://www.w3schools.com/python/module_random.asp
# Import the random module, and display a random number between 1 and 9:
import random


# Result: 1 2 3 4 5.
i = 1
while i < 6:
    print(i)
    i = i + 1
# i = i + 1
# is the same like
# i += 1


# break
# Break in case when i = 3.
# Result: 1 2 3.
i = 1
while i < 6:
    print(i)
    if (i == 3):
        break
    i += 1


# continue
# Skip number, in our case 3.
# Result: 1 2 4 5 6.
i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)
# Note that number 3 is missing in the result.


# else
# Result: 3 4 5 i is no longer less than 6.
i = 3
while i < 6:
    print(i)
    i += 1
else:
    print("i is no longer less than 6")




# EXAMPLES:


# 1
# Result: 9 11 12 13 14 15.
i = 8
while i < 15:
    i = i + 1
    if i == 10:
        continue
    print(i)