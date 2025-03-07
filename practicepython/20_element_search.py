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
# REQUESTS PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install requests
import requests
# BEAUTIFUL SOUP PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install bs4
from bs4 import BeautifulSoup


# Write a function that takes an ordered list of numbers and another number.
# The function decides whether the given number is inside the ordered list and returns and then prints an appropriate boolean.


# Task MODEL or TEMPLATE
# Try to find out, whether the "number" is in the defined list.
# Then print boolean value True / False.
def find(ordered_list, element_to_find):

    for element in ordered_list:
        if element == element_to_find:
            return True
    return False


if __name__=="__main__":

    l = [2, 4, 6, 8, 10]

    print(find(l, 5)) # prints False
    print(find(l, 10)) # prints True
    print(find(l, -1)) # prints False
    print(find(l, 2)) # prints True

# Empty row.
print()


# Task 1
# Try to find out, whether the "number" is in the defined list.
# Then print boolean value True / False.
def my_function():

    x = [1, 3, 5, 30, 42, 43, 500]
    
    value = True

    while True:
        number = input("Task 1: Give me your digit: ")
        number = int(number)
        if number not in x:
            print("Task 1: Incorrect answer")
            value = False
            print(value)
            continue
        else:
            print("Task 1: Correct answer")
            value = True
            print(value)
            break
    
    return


my_function()

# Empty row.
print()


# Task 2
# Try to find out, whether the "number" is in the defined list. Using "Binary search".
def my_function_with_binary_search():

    x = [11, 38, 58, 301, 425, 432, 5000]
    #print(x)

    value = True

    while True:
        
        number = input("Task 2: Give me your digit: ")
        number = int(number)
        
        x_list_middle_item = x[len(x)//2]
        if len(x) % 2 == 1:
            print("Just for information, middle of x list: " + str(x_list_middle_item))
        else:
            print("Task 2: Number of list items is even, therefore it is unable to set the middle of the list.")
            break

        if number == x_list_middle_item:
            print("Task 2: Result is: " + str(x_list_middle_item) + ", correct answer.")
            value = True
            break

        elif number < x_list_middle_item:
            y = x[0:(len(x)//2)]
            #print(y)
            y_list_middle_item = y[len(y)//2]
            print("Just for information, middle of y list: " + str(y_list_middle_item))
            if number == y_list_middle_item:
                print("Task 2: Result is: " + str(y_list_middle_item) + ", correct answer.")
                value = True
                break
            elif number < y_list_middle_item:
                z = y[0]
                if number not in x:
                    value = False
                    continue
                else:
                    print("Task 2: Correct answer")
                    value = True
                    break
            else:
                z = y[2]
                if number not in x:
                    value = False
                    continue
                else:
                    print("Task 2: Correct answer")
                    value = True
                    break

        else:
            y = x[((len(x)//2)+1):]
            #print(y)
            y_list_middle_item = y[len(y)//2]
            print("Just for information, middle of y list: " + str(y_list_middle_item))
            if number == y_list_middle_item:
                print("Task 2: Result is: " + str(y_list_middle_item) + ", correct answer.")
                value = True
                break
            elif number < y_list_middle_item:
                z = y[0]
                if number not in x:
                    value = False
                    continue
                else:
                    print("Task 2: Correct answer")
                    value = True
                    break
            else:
                z = y[2]
                if number not in x:
                    value = False
                    continue
                else:
                    print("Task 2: Correct answer")
                    value = True
                    break

    return


my_function_with_binary_search()