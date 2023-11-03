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
# SLIDER PURPOSES - IN THIS SCRIPT
from selenium.webdriver.common.action_chains import ActionChains
# RANDOM PURPOSES
# https://www.w3schools.com/python/module_random.asp
# Import the random module, and display a random number between 1 and 9:
import random


# 0  \n

# This \n is hidden but present at the end of each print statement. It is the same like enter in word, it means go to new line.

# Example 1

print("Hello", end = ' ')
print("World!")
# Result: Hello World!
# Default value would be: end='\n'. It means go to new line.

# Example 2

print("Hello")
print("World!")
# Result:
# Hello
# World!


# 1
# Result is: 0, 1, 2, 3, 4, 5.
x = range(6)

for n in x:
  print(n)


# 2
# Result is: llo.
b = "Hello, World!"
print(b[2:5])


# 3
# Returns "Hello, World!".
a = " Hello, World! "
print(a.strip())


# 4
# Returns "HELLO, WORLD!".
a = "Hello World!"
print(a.upper())
# Returns "hello, world!".
a = "Hello World!"
print(a.lower())


# 5
# Returns "Jello World!".
a = "Hello World!"
print(a.replace("H", "J"))


# 6
age = 36
txt = "My name is Robert, and I am {}"
print(txt.format(age))


# 7
quantity = 3
itemno = 567
price = 49.95
myorder = "I want to pay {2} dollars for {0} pieces of item {1}."
print(myorder.format(quantity, itemno, price))


# 8
txt = "We are the so-called \"Vikings\" from the north."
print(txt)


# 9  IN, NOT IN
# Returns True because the value "banana" is in the list.
# Returns True because the value "pinaple" is not in the list.
x = ["apple", "banana"]
print("banana" in x)
print("pinaple" not in x)


# 10  IS, IS NOT
x = ["apple", "banana"]
y = ["apple", "banana"]
z = x
# Returns True because z is the same object as x.
print(x is z)
# Returns False because x is not the same object as y, even if they have the same content.
print(x is y)
# To demonstrate the difference betweeen "is" and "==": this comparison returns True because x is equal to y.
print(x == y)


# 11  AND, OR, NOT
x = 5
# Returns True because 5 is greater than 3 AND 5 is less than 10.
print(x > 3 and x < 10)
# Returns True because one of the conditions is true (5 is greater than 3, but 5 is not less than 4).
print(x > 3 or x < 4)
# Returns False because NOT is used to reverse the result.
print(not(x > 3 and x < 10))


# 12
thislist = ["apple", "banana", "cherry"]
print(len(thislist))

thistuple = ("apple", "banana", "cherry")
print(len(thistuple))