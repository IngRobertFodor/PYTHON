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


# Print each fruit in a fruit list.
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)

# Loop through the letters in the word "banana".
for x in "banana":
  print(x)


# range()
# Result: 0 1 2 3 4 5.
for x in range(6):
  print(x)

# Increment the sequence with 3 (default is 1).
# Result: 8 11 14 17 20 23 26 29.
for x in range(8, 30, 3):
  print(x)


# break continue
# Exit the loop when x is "banana", after banana.
# Result: apple banana.
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x) 
  if x == "banana":
    break

# Exit the loop when x is "banana", but this time the break comes before the print.
# Result: apple.
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    break
  print(x)

# Do not print banana.
# Result: apple cherry.
fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    continue
  print(x)


# else
# Print all numbers from 0 to 5, and print a message when the loop has ended.
# Result 0 1 2 3 4 5 Finally finished!.
for x in range(6):
  print(x)
else:
  print("Finally finished!")

# Result: 0 1 2.
for x in range(6):
  if x == 3:
    break
  print(x)
else:
  print("Finally finished!")
# If the loop breaks, the else block is not executed.

# Result: 0 1 2.
for x in range(6):
  if x == 3: break
  print(x)
else:
  print("Finally finished!")
# If the loop breaks, the else block is not executed.


#  NESTED
# Print each adjective for every fruit.
# Result:
# red apple
# red banana
# red cherry
# big apple
# big banana
# big cherry
# tasty apple
# tasty banana
# tasty cherry.
adj = ["red", "big", "tasty"]
fruits = ["apple", "banana", "cherry"]
for x in adj:
  for y in fruits:
    print(x, y)