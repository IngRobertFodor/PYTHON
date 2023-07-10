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
# MATH PURPOSES - Fractions
import fractions
# SEARCH PURPOSES (RegEx)
import re
# DELETE, FILE HANDLING PURPOSES
import os
# MATPLOTLIB, VISUALIZATION PURPOSES
import matplotlib
# MYSQL PURPOSES
import mysql.connector


# Write a program that asks the user how many Fibonacci numbers to generate and then generates them.
# The Fibonacci sequence is a sequence of numbers, where the next number in the sequence is the sum of the previous two numbers in the sequence.
# The sequence looks like this: 0, 1, 1, 2, 3, 5.

# Ask user how many Fibonacci numbers to generate.
how_many_numbers = input("Give me your number: ")
print("You want " + how_many_numbers + " Fibonacci numbers.")
how_many_numbers = int(how_many_numbers)

# Create empty list.
new_list = []
print(new_list)
# Add "0" to empty list. "0" would be missing.
new_list.insert(0, 0)
print(new_list)

def my_function():    
    n1, n2 = 0, 1
    sum = int()
    # Here I am going to validate the user input.
    if how_many_numbers <= 0:
        print("Number should be greater than 0.")
    # Fibonacci
    for i in range(0, how_many_numbers):
        n1 = n2
        n2 = sum
        sum = n1 + n2
        new_list.append(sum)
    print(new_list)
    # Here I will check and correct the lenght of the final list.
    if len(new_list) >= how_many_numbers:
        print(new_list[0:how_many_numbers])

my_function()