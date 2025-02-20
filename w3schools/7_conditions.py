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


# 1  IF ELIF ELSE

# 1.1
# IF
# ELIF
# ELSE
a = 200
b = 33
if b > a:
    print("b is greater than a")
elif a == b:
    print("a and b are equal")
else:
    print("a is greater than b")

# 1.2 Shortened version (= Ternary Operators or Conditional Expressions).
# Example 1
a = 2
b = 330
print("A") if a > b else print("B")
# Example 2
a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")


# 2  AND
a = 200
b = 33
c = 500
if a > b and c > a:
    print("Both conditions are True")


# 3  OR
a = 200
b = 33
c = 500
if a > b or b > c:
    print("At least one of the conditions is True")


# 4  NOT
a = 33
b = 200
if not a > b:
    print("a is NOT greater than b")


# 5  NESTED IF
x = 41
if x > 10:
    print("Above ten,", end=" ")
    if x > 20:
        print("and also above 20!")
    else:
        print("but not above 20.")