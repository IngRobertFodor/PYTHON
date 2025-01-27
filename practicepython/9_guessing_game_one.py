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


def play_game():
    tuple_a = tuple(range(1,10))
    print(tuple_a)

    random_number = random.randint(1,9)
    print(random_number)

    count = 0
    
    while True:

        guess_random_number = int(input("Guess a random number between 1 and 9 (including 1 and 9): "))
        
        if guess_random_number not in tuple_a:   
            print("Number not from interval (1 to 9).")
            count+=1

        elif guess_random_number == "Exit":
            break

        elif random_number > guess_random_number:
            print("You guessed too small number.")
            count+=1

        elif guess_random_number > random_number:
            print("You guessed too big number.")
            count+=1

        else:
            # random_number == guess_random_number
            guess_random_number = str(guess_random_number)
            print("This is the right guess: " + guess_random_number + ". This was the random number.")
            count+=1
            print(count)

            return


play_game()