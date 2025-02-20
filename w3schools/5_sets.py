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


# Number 1 and True are considered to be the same values in sets.
# Duplicates are ignored.


# 1  LEN
# len()
# Shows the number of items in set.
thisset = {"apple", "banana", "cherry"}
print(len(thisset))


# 2  LOOPS

# 2.1  FOR LOOP
thisset = {"apple", "banana", "cherry"}
for x in thisset:
    print(x)


# 3  Add items to set

# add()
thisset = {"apple", "banana", "cherry"}
thisset.add("orange")
print(thisset)

# update()
thisset = {"apple", "banana", "cherry"}
tropical = {"pineapple", "mango", "papaya"}
thisset.update(tropical)
print(thisset)


# 4  Remove items from set

# remove()
# If the item to remove does not exist, remove() will raise an error.
thisset = {"apple", "banana", "cherry"}
thisset.remove("banana")
print(thisset)

# discard()
# If the item to discard does not exist, discard() will not raise an error.
thisset = {"apple", "banana", "cherry"}
thisset.discard("banana")
print(thisset)

# pop()
thisset = {"apple", "banana", "cherry"}
x = thisset.pop()
print(x) #removed item
print(thisset) #the set after removal

# clear()

# del


# 5  JOIN

# update()
set1 = {"a", "b" , "c"}
set2 = {1, 2, 3}
set1.update(set2)
print(set1)

# union()
set1 = {"a", "b" , "c"}
set2 = {1, 2, 3}
set3 = set1.union(set2)
print(set3)