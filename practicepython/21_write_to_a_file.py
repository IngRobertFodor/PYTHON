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


# 1
# This is considered WORSE programming practice.
# In this code example, the file object will be opened, saved and then closed manually.
# Because in case of error in the program, it terminates before hitting the ".close()" statement.
my_file = open("file_to_save_one.txt", "w")
# Opening a file for writing with "w" will overwrite any file that currently exists with that name.
my_file.write("1: This is my text.")
my_file.close()

# 2.1
# This is considered CORRECT programming practice.
# As soon as the program exists the with code block for any reason, it will close the file.
# Opening a file for writing with "w" will overwrite any file that currently exists with that name.
with open("file_to_save_two.txt", "w") as open_file:
    open_file.write("2.1: This is my text.")

# 2.2
# User should define file name.
user_defined_file_name = input("Define the name of your file: ")
with open(user_defined_file_name, "w") as open_file:
    open_file.write("2.2: This is my text.")