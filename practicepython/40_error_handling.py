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
from matplotlib import pyplot as plt
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
# JSON PURPOSES (WORKING WITH FILES)
import json


def play_game():
    tuple_a = range(1,10)
    tuple_a = tuple(tuple_a)
    print(tuple_a)

    random_number = random.randint(1,9)
    print(random_number)

    count = 0
    
    while True:

        try:
            guess_random_number = input("Guess a random number between 1 and 9 (including 1 and 9): ")
            if int(guess_random_number) in tuple_a:
                # I will count these guesses.
                count+=1
                if random_number > int(guess_random_number):
                    print("You guessed too small number.")
                elif int(guess_random_number) > random_number:
                    print("You guessed too big number.")
                else:
                    # random_number == int(guess_random_number)
                    print(f"This is the right guess: {guess_random_number}. This was the random number.")
                    print(f"You needed {count} guesses.")  
                    break 
            elif int(guess_random_number) not in tuple_a:
                # I won´t count these guesses.
                print("Number not from interval (1 to 9). Guess again.")
        
        except ValueError:
            # Testing whether guess is a number. Guess like e.g. testing will throw ValueError.
            # I won´t count these guesses.
            print("ValueError, guess is not a number.")
            if guess_random_number == "EXIT":
                print("User don´t want to play.")
                break


    return


play_game()