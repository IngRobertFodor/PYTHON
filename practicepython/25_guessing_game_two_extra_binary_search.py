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


# The Fourth best way for PC to guess.
# Using "Binary search".      
def play_game_four_binary_search(list_a, my_number, low=None, high=None, count=0):
    
    if low is None:
        low = 0
    if high is None:
        high = len(list_a) - 1
    if high < low:
        return False
    
    midpoint = (low + high) // 2
    # Our midpoint is 49, because "list_a[49] == 50".
    if list_a[midpoint] == my_number:
        count += 1
        return count
    
    elif my_number < list_a[midpoint]:
        new_high = midpoint - 1
        count += 1
        return play_game_four_binary_search(list_a, my_number, low, new_high, count)

    else:
        # elif my_number > list_a[midpoint]:
        new_low = midpoint + 1
        count += 1
        return play_game_four_binary_search(list_a, my_number, new_low, high, count)    


if __name__ == "__main__":
    # The Fourth best way for PC to guess.
    # Using "Binary search".
    
    # List of digits 1-100 (including 1 and 100).
    list_a = list(range(1,101))
    my_number = 88
    print("PC needed this many guesses.")
    print(play_game_four_binary_search(list_a, my_number))
