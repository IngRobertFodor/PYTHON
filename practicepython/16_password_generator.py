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
# SLIDER PURPOSES
from selenium.webdriver.common.action_chains import ActionChains
# RANDOM PURPOSES
# https://www.w3schools.com/python/module_random.asp
# Import the random module, and display a random number between 1 and 9:
import random
# STRING PURPOSES
import string
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


# User tells us, how long should be the password.
password_length = input("How long should be Your password?: ")
print("You picked the length " + password_length + ".")
password_length = int(password_length)

# Default password list, to select password from.
default_pwd_options = ["Asdfg", "Gfdsa", "Qwert", "Trewq"]
default_password = random.choice(default_pwd_options)
#print("Your default password is " + default_password + ".")

# Write a password generator in Python. This function does that.
def new_pwd():
    
    generated_password = []
    possible_choices = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    while len(generated_password) < password_length:
        random_choice = random.choice(possible_choices)
        generated_password.append(random_choice)
    new_generated_password = "".join(generated_password)
    return print("Your new password is " + new_generated_password + ".")

# Length of password defined by user in input string. It predefines, how will the password look like.
if password_length <= 5:
    print("Your new password is one of the defaults: " + default_password + ".")
elif password_length > 5 and password_length <= 15:
    new_pwd()
else:
    print("The maximal password length is 15.")