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


# Ask the user for a number and determine whether the number is prime or not (0-20).
# Prime number is a number that has no divisors.

# Ask user for his number.
my_number = input("Give me some number: ")
print("Your number was " + my_number + ".")
my_number = int(my_number)

# List all prime numbers to 20.
prime_numbers_list_to_twenty = [2,3,5,7,11,13,17,19]

def find_prime_num():
    if my_number in prime_numbers_list_to_twenty:
            print("The " + str(my_number) + " is prime number.")
    else:
            print("Guess other number to find the prime numbers from 0 to 20.")
    
find_prime_num()


# Number 1 is not prime number.
# Extra exercise to list all prime numbers to 100.
prime_numbers_list_to_onehundred = []
for num in range(2,101):
    prime = True
    for i in range(2,num):
        if (num%i==0):
            prime = False
    if prime:
       print(num)
       prime_numbers_list_to_onehundred.append(num)

print(prime_numbers_list_to_onehundred)