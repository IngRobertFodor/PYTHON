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


# Exercise 1
# Write a function that prints back the string with the words in backwards order.
a = "My name is Michele"
aa = "My name is Nicky"

def reversed_order_version1(x):
    list_a = x.split()
    list_a.reverse()
    print(list_a)
    return

reversed_order_version1(a)
reversed_order_version1(aa)


# Exercise 2
# Write a program (function) that asks user for a string containing multiple words.
# Print back the same string with the words in backwards order.
def reversed_order_version2():
    x = input("Give me Your name and surname: ")
    print("Your name is " + x + ".")

    list_a = x.split()
    list_a.reverse()
    reversed_list_a = ' '.join(list_a)
    print(reversed_list_a)
    return print("Your reversed name is " + reversed_list_a + ".")

reversed_order_version2()