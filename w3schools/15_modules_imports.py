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


# 1  import variablesfunctions as vf (My own module)

# Alias means that you can use full name or alias, not both.
import variablesfunctions as vf
# You can import everything from the module or just something, like: "person1" dictionary.
from variablesfunctions import person1

# 1.1
vf.my_function_to_test_import()

# 1.2
a = vf.person1["age"]
print(a)
print(person1["age"])

# 1.3
# This lists all methods that we have imported using "import variablesfunction as vf".
x = dir(vf)
print(x)


# 2  import datetime (Built in module)

# 2.1
# Current date
x = datetime.datetime.now()
print(x)

# 2.2
# Returns the year and name of weekday
x = datetime.datetime.now()
print(x.year)
print(x.strftime("%A"))

# 2.3
x = datetime.datetime(2020, 5, 18)
print(x)

# 2.4
# Display the name of the month.
x = datetime.datetime(2018, 2, 1)
print(x.strftime("%B"))


# 3  import math

# 3.1
x = min(5, 10, 25)
y = max(5, 10, 25)
print(x) # returns 5
print(y) # returns 25

# 3.2
x = abs(-8.25)
print(x) # returns 8,25

# 3.3
x = pow(4, 3)
print(x) # returns 64 (4 * 4 * 4 = 64)

# 3.4
x = math.ceil(1.4)
y = math.floor(1.4)
print(x) # returns 2
print(y) # returns 1

# 3.5
x = math.pi
print(x)


# 4  import re
# RegEx

# 4.1 search()
# Check if the string starts with "The" and ends with "Spain".
txt = "The rain in Spain"
x = re.search("^The.*Spain$", txt)
if x:
  print("YES! We have a match!")
else:
  print("No match")
# Result: YES! We have a match!.

# 4.2 split()
# The split() function returns a list where the string has been split at each match.
txt = "The rain in Spain"
x = re.split("\s", txt)
print(x)
# Result: ['The', 'rain', 'in', 'Spain'].

# Split the string only at the first occurrence.
txt = "The rain in Spain"
x = re.split("\s", txt, 1)
print(x)
# Result: ['The', 'rain in Spain'].

# 4.3 sub()
# Replace all white-space characters with the digit "8".
txt = "The rain in Spain"
x = re.sub("\s", "8", txt)
print(x)
# Result: [The8rain8in8Spain].

# Replace the first 2 occurrences.
txt = "The rain in Spain"
x = re.sub("\s", "8", txt, 2)
print(x)
# Result: [The8rain8in Spain].

# 4.4 # search() span()
# The Match object has properties and methods used to retrieve information about the search, and the result.
# Search for an upper case "S" character in the beginning of a word, and print its position.
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.span())
# Result: (12, 17).

# 4.5 search() string()
# The Match object has properties and methods used to retrieve information about the search, and the result.
# The string property returns the search string.
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.string)
# Result: The rain in Spain.

# 4.6 search() group()
# The Match object has properties and methods used to retrieve information about the search, and the result.
# Search for an upper case "S" character in the beginning of a word, and print the word.
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.group())
# Result: Spain.