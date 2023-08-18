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


# As a parameter of a function I write "my number". The pc will guess what "my number" was. And then pc counts guesses that pc needed to find "my number".

# First way for PC to guess.
def play_game_one(my_guess):

    # List of digits 1-100 (including 1 and 100).
    list_a = list(range(1,101))
    
    count = 0 
         
    while True:    
        
        pc_guess_random_number_one = random.randrange(1,101)
        
        if my_guess > pc_guess_random_number_one or pc_guess_random_number_one > my_guess:
            print("PC guessed wrong number.")
            count+=1
            continue
        else:
            pc_guess_random_number_one == my_guess
            print("This is the right guess: " + str(pc_guess_random_number_one) + ". This was my_guess.")
            count+=1
            print(count)
            break
     
    return


# Second way for PC to guess.
def play_game_two(my_guess):

    # List of digits 1-100 (including 1 and 100).
    list_a = list(range(1,101))
    
    count = 0

    while True:
        
        for pc_guess_random_number_two in list_a:
        
            if my_guess > pc_guess_random_number_two:
                print("PC guessed too small number.")
                count+=1

            else:
                pc_guess_random_number_two == my_guess
                print("This is the right guess: " + str(pc_guess_random_number_two) + ". This was my_guess.")
                count+=1
                print(count)
                break

        return

        
# Third way for PC to guess.      
def play_game_three(my_guess):

    # List of digits 1-100 (including 1 and 100).
    list_a = list(range(1,101))
    
    count = 0
    pc_guess_random_number_three = ""

    while True:
        
        # pc_guess_random_number_three = 50 (This is the middle of the interval.)
        pc_guess_random_number_three = len(list_a)//2
        
        while my_guess != pc_guess_random_number_three:

            if my_guess < pc_guess_random_number_three:
                pc_guess_random_number_three = pc_guess_random_number_three-1
                print(pc_guess_random_number_three)
                count+=1
                if pc_guess_random_number_three == my_guess:
                    print(f"PC needed {count} guesses.")
                    break
            elif my_guess > pc_guess_random_number_three:
                pc_guess_random_number_three = pc_guess_random_number_three+1
                print(pc_guess_random_number_three)
                count+=1
                if pc_guess_random_number_three == my_guess:
                    print(f"PC needed {count} guesses.")
                    break

        return


# The Fourth best way for PC to guess.
# Using "Binary search".      
def play_game_four_binary_search(list_a, my_number, low=None, high=None, count=0):
    
    if low is None:
        low = 0
    if high is None:
        high = len(list_a) - 1
    if high < low:
        return False
    
    while True:
        midpoint = (low + high) // 2
        # Our midpoint is 49, because "list_a[49] == 50".
        if my_number > list_a[midpoint]:
            new_low = midpoint + 1
            count += 1
            return play_game_four_binary_search(list_a, my_number, new_low, high, count) 
        
        elif my_number < list_a[midpoint]:
            new_high = midpoint - 1
            count += 1
            return play_game_four_binary_search(list_a, my_number, low, new_high, count)
        
        else:
            # list_a[midpoint] == my_number:
            count += 1
            return count
    

if __name__ == "__main__":
    
# First way for PC to guess.    
    # The number of guesses is everytime different.
    play_game_one(80)
    # e.g. 120
    play_game_one(80)
    #  e.g. 25

    # Empty row.
    print()

# Second way for PC to guess.
    # The number of guesses is everytime the same (55).
    play_game_two(55)
    # e.g. 55
    play_game_two(55)
    # e.g. 55

    # Empty row.
    print()

# Third way for PC to guess.
    play_game_three(38)
    play_game_three(88)

    # Empty row.
    print()

# The Fourth best way for PC to guess.
# Using "Binary search".
    # List of digits 1-100 (including 1 and 100).
    list_a = list(range(1,101))
    my_number = 88
    print("PC needed this many guesses.")
    print(play_game_four_binary_search(list_a, my_number))