# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# FINDING ELEMENTS PURPOSES
#   !!! RUN THIS FIRST (CMD)
#   pip install htmldom==2.0
from htmldom import htmldom
# TEXT PURPOSES
from selenium.webdriver.common.keys import Keys
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
#   Shortened version of code (as).
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
#       https://www.w3schools.com/python/module_random.asp
import random
# STRING PURPOSES
import string
# MATH PURPOSES
#       https://www.w3schools.com/python/module_math.asp
#       https://docs.python.org/3/library/math.html
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
#   !!! RUN THIS FIRST (CMD)
#   pip install requests
import requests
# BEAUTIFUL SOUP PURPOSES
#   !!! RUN THIS FIRST (CMD)
#   pip install bs4
from bs4 import BeautifulSoup
# COLLECTIONS PURPOSES
import collections


def play_cows_and_bulls_game():


    # Generate random 4-digits number.
    # Create tuple of possible digits.
    digits = (1,2,3,4,5,6,7,8,9)
    print(digits)
    # Use random module to generate 4 different digits.
    random_number_digits = random.sample(digits, 4)
    print(random_number_digits)
    # This joins and prints random 4-digits number.
    random_number = ''.join(map(str, random_number_digits))
    print("This is random generated 4-digit number: " + str(random_number) + ".")

    guesses = 0
    playing = True
    while playing:

        # Ask user to guess the generated number.
        users_guess = int(input("GUESS the generated 4-digit number: "))
        print("User guessed this number: " + str(users_guess) + ".")
        guesses +=1
        users_guess = str(users_guess)

        cows = 0
        bulls = 0
        
        for i in range(len(random_number)):
            if random_number[i] == users_guess[i]:
                cows +=1
            else:
                bulls +=1

        if cows == 4:
            print("You won.")
            playing = False

        print(cows, bulls, guesses)

    return
    

if __name__=="__main__":    
    play_cows_and_bulls_game()