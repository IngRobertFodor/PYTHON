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


# Change the values "banana" and "cherry" with the values "blackcurrant" and "watermelon".
thislist = ["apple", "banana", "cherry", "orange", "kiwi", "mango"]
thislist[1:3] = ["blackcurrant", "watermelon"]
print(thislist)

# Change the second value by replacing it with two new values.
thislist = ["apple", "banana", "cherry"]
thislist[1:2] = ["blackcurrant", "watermelon"]
print(thislist)

# Change the second and third value by replacing it with one value.
thislist = ["apple", "banana", "cherry"]
thislist[1:3] = ["watermelon"]
print(thislist)


# 1  LIST COMPREHENSION

# Result is: ['apple', 'banana', 'mango'].
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = [x for x in fruits if "a" in x]
print(newlist)

# Result is: ['APPLE', 'BANANA', 'CHERRY', 'KIWI', 'MANGO'].
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = [x.upper() for x in fruits]
print(newlist)

# Result is: ['hello', 'hello', 'hello', 'hello', 'hello'].
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = ['hello' for x in fruits]
print(newlist)


# 2  SORT

# Sort str, int.
thislistone = ["orange", "mango", "kiwi", "pineapple", "banana"]
thislistone.sort()
print(thislistone)
thislisttwo = [100, 50, 65, 82, 23]
thislisttwo.sort()
print(thislisttwo)

# Sort in reverse order. 
thislist = ["orange", "mango", "kiwi", "pineapple", "banana"]
thislist.sort(reverse = True)
print(thislist)

# Case-sensitive sort, capital letters being sorted before lower case.
thislist = ["banana", "Orange", "Kiwi", "cherry"]
thislist.sort()
print(thislist)

# Case-insensitive sort.
thislist = ["banana", "Orange", "Kiwi", "cherry"]
thislist.sort(key = str.lower)
print(thislist)

# Reverse order.
thislist = ["banana", "Orange", "Kiwi", "cherry"]
thislist.reverse()
print(thislist)


# 3  COPY

# copy()
thislist = ["apple", "banana", "cherry"]
mylist = thislist.copy()
print(mylist)

# list()
thislist = ["apple", "banana", "cherry"]
mylist = list(thislist)
print(mylist)


# 4  JOIN

# +
list1 = ["a", "b", "c"]
list2 = [1, 2, 3]
list3 = list1 + list2
print(list3)

# extend()
list1 = ["a", "b" , "c"]
list2 = [1, 2, 3]
list1.extend(list2)
print(list1)

# append()
list1 = ["a", "b" , "c"]
list2 = [1, 2, 3]
for x in list2:
    list1.append(x)
print(list1)


# 5  LOOPS

# 5.1  FOR LOOP
thislist = ["apple", "banana", "cherry"]
for x in thislist:
  print(x)

# 5.2  WHILE LOOP
thislist = ["apple", "banana", "cherry"]
i = 0
while i < len(thislist):
  print(thislist[i])
  i = i + 1


# 6  LEN
# len()
# Shows the number of items in list.
thislist = ["apple", "banana", "cherry"]
print(len(thislist))