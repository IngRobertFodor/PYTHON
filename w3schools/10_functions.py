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


'''
From a function's perspective:
A parameter is the variable listed inside the parentheses in the function definition.
An argument is the value that is sent to the function when it is called.
'''


# PASS
def myfunction():
  pass
# having an empty function definition like this, would raise an error without the pass statement


#
def my_function():
  print("Hello from a function")

my_function()


#
def my_function(fname):
  print(fname + " Refsnes")

my_function("Tom")
my_function("Tobias")
my_function("Linus")


#
def my_function(fname, lname):
  print(fname + " " + lname)

my_function("Tom", "Refsnes")


#
def my_function(*kids):
  print("The youngest child is " + kids[2])

my_function("Tom", "Tobias", "Linus")


#
def my_function(child3, child2, child1):
  print("The youngest child is " + child3)

my_function(child1 = "Tom", child2 = "Tobias", child3 = "Linus")


#
def my_function(**kid):
  print("His last name is " + kid["lname"])

my_function(fname = "Tom", lname = "Refsnes")


# If we call the function without argument, it uses the default value.
def my_function(country = "Norway"):
  print("I am from " + country)

my_function("Sweden")
my_function("India")
my_function()
my_function("Brazil")


# You can send any data types as argument to a function.
food = ["apple", "banana", "cherry"]

def my_function(food):
  for x in food:
    print(x)

my_function(food)


#
def my_function(x):
  return 5 * x

print(my_function(3))
print(my_function(5))
print(my_function(9))


# Examples 1
def get_integer(help_text="Give me a number: "):
    return int(input(help_text))

age = get_integer("Tell me your age: ")
school_year = get_integer()

if age > 15:
  print("You are over the age of 15")

print("You are in grade " + str(school_year))


# Examples 2

# Same results for 2.1, 2.2, 2.3.

# Examples 2.1
def make_even(num):
  if num % 2 == 1:
    return num + 1
  else:
    return num

x = [551, 641, 891, 122, 453, 223, 234, 343, 562, 115, 554, 679, 516]

y = []
for num in x:
  y.append(make_even(num))

print(y)


# Examples 2.2
def make_even(num):
  if num % 2 == 1:
    return num + 1
  else:
    return num

x = [551, 641, 891, 122, 453, 223, 234, 343, 562, 115, 554, 679, 516]

y = [make_even(num) for num in x]

print(y)


# Examples 2.3
def make_even(num):
  if num % 2 == 1:
    return num + 1
  else:
    return num

x = [551, 641, 891, 122, 453, 223, 234, 343, 562, 115, 554, 679, 516]

y = list(map(make_even, x))

print(y)