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
# SLIDER PURPOSES
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

    
    # collections (collections.Counter)
    # Counter is used to keep the count of the elements in an iterable in the form of an unordered dictionary
    # The key represents the element in the iterable and the value represents the count of that element in the iterable.
    # Example to describe how it works.
        # print(Counter(['B','B','A','B','C','A','B','B','A','C']))
        # Counter({'B': 5, 'A': 3, 'C': 2})
    x = collections.Counter(random_number)
    
    count = 1
    

    while True:

        cows = 0
        bulls = 0

        # Ask user to guess the generated number.
        users_guess = int(input("GUESS the generated 4-digit number: "))
        print("User guessed this number: " + str(users_guess) + ".")

        if users_guess not in range(1000,9999):   
            print("Number doesn't have 4-digits.")
            count +=1
            continue

        # zip()
        # Python’s zip() function creates an iterator that will aggregate elements from two or more iterables.
        # Example to describe how it works.
            # numbers = [1, 2, 3]
            # letters = ['a', 'b', 'c']
            # zipped = zip(numbers, letters)
            # print(list(zipped))
            # [(1, 'a'), (2, 'b'), (3, 'c')]
        elif random_number != str(users_guess):                      
            for a, b in zip(random_number, str(users_guess)):
                if a == b:
                    cows +=1
                    x[b] +=1
            for a, b in zip(random_number, str(users_guess)):
                if a != b and x[b] > 0:
                    bulls +=1
                    x[b] +=1
            print(cows,bulls,count)
            count +=1
            continue
            
        else:
            # random_number == users_guess
            users_guess = str(users_guess)
            print("This is the right guess: " + str(users_guess) + ". This was the 4-digit random number.")
            print("4 cows, 0 bulls, " + str(count) + " guesses.")
            cows = 4
            break


    return
    

if __name__=="__main__":    
    play_cows_and_bulls_game()