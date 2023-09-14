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
# REQUESTS PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install requests
import requests
# BEAUTIFUL SOUP PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install bs4
from bs4 import BeautifulSoup
# COLLECTIONS PURPOSES
import collections


with open("birthday_dictionaries.txt", "r") as open_file:
    my_string = open_file.read()
    print(my_string)
    print(type(my_string))
    

    # DICTIONARY 1 "my_dictionary"
    # Keys for "my_dictionary".
    keys = my_string[0:23]
    print(keys)
    keys_list = keys.split(",")
    print(keys_list)
    # Values for "my_dictionary"
    values = my_string[24:67]
    print(values)
    values_list = values.split(",")
    print(values_list)
    # Create dictionary "my_dictionary".
    my_dictionary = {keys_list[i]: values_list[i] for i in range(0, len(keys_list))}
    print(my_dictionary)
    print(type(my_dictionary))
    print(my_dictionary.keys())
    print(my_dictionary.values())


    # DICTIONARY 2  "my_eval_dictionary".
    # "EVAL" was used to convert string to dictionary.
    birthdays = my_string[69:]
    print(type(birthdays))
    print(birthdays)
    my_eval_dictionary = eval(birthdays)
    print(type(my_eval_dictionary))
    print(my_eval_dictionary)


    # Ask user what he wants to see.
    user = input("Who's birthday do you want to look up?: ")
    
    # Only one of these two print statements can be in use at a time, because it wouldn´t work.
    # print(my_dictionary[user])
    print(my_eval_dictionary[user])