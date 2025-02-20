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


# 0  LIST, TUPLE, SET, DICTIONARY

# List is a collection which is ordered and changeable. Allows duplicate members.
# Tuple is a collection which is ordered and unchangeable. Allows duplicate members.
# Set is a collection which is unordered, unchangeable, and unindexed. No duplicate members.
# Dictionary is a collection which is ordered and changeable. No duplicate members.


# 1  Add items to tuple

# 1.1  Convert it to the list. Add item or items to the list. And convert it back to tuple.
x = ("apple", "banana", "cherry")
y = list(x)
y[1] = "kiwi"
x = tuple(y)
print(x)

# 1.2  Create a new tuple with the value "orange", and add that tuple
thistuple = ("apple", "banana", "cherry")
# When creating a tuple with only one item, remember to include a comma after the item.
# Otherwise it will not be identified as a tuple. (It would be: str)
y = ("orange",)
thistuple += y
print(thistuple)


# 2  Remove items from tuple

# 2.1  Convert it to the list. Remove item or items from the list. And convert it back to tuple.
thistuple = ("apple", "banana", "cherry")
y = list(thistuple)
y.remove("apple")
thistuple = tuple(y)
print(thistuple)


# 3  LOOPS

# 3.1  FOR LOOP
thistuple = ("apple", "banana", "cherry")
for x in thistuple:
    print(x)

# 3.2  WHILE LOOP
thistuple = ("apple", "banana", "cherry")
i = 0
while i < len(thistuple):
    print(thistuple[i])
    i += 1


# 4  JOIN

# +
tuple1 = ("a", "b" , "c")
tuple2 = (1, 2, 3)
tuple3 = tuple1 + tuple2
print(tuple3)

# *
fruits = ("apple", "banana", "cherry")
mytuple = fruits * 2
print(mytuple)


# 5  LEN
# len()
# Shows the number of items in tuple.
thistuple = ("apple", "banana", "cherry")
print(len(thistuple))