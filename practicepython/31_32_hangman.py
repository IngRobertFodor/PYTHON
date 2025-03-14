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
# COLLECTIONS PURPOSES
import collections


# First Code Example. Only words with unique letters are here.
print("First way")
print()

count = 0
# Words to pick up from in this game.
# Only words with unique letters are here (e.g. "SLOVAKIA" has "A" and "A", therefore it is not here.).
word_to_guess = ["BOAT", "USA", "HOME", "COMPUTER", "DOG"]
word_to_guess = random.choice(word_to_guess)
print(word_to_guess)
word_to_guess = list(word_to_guess)
# This will be the "word from letters that user guessed".
word_from_letters_guessed = list("_" * len(word_to_guess))
# We have lists, where we can find items by its index now.
print("Word to Guess:", word_to_guess)
print("Word from letters guessed:", word_from_letters_guessed)
# This shows each letter and number of its occurences in "word_to_guess".
a = [[x,word_to_guess.count(x)] for x in word_to_guess]
print(a)

while True:
    print("Welcome to Hangman´s game.")
    user_guessed_letter = input("Guess the LETTER: ")
    print(user_guessed_letter)
    
    if user_guessed_letter not in string.ascii_uppercase or user_guessed_letter not in word_to_guess:
        count +=1
        print(f"Not a letter, not in uppercase or other wrong guess. This was your {count} wrong guess.")
        # "count >= 7" wrong guesses (One per each letter in "hagnman".).
        if count >= 7:
            print(f"You are hanged. This was your {count} wrong guess.")
            break
    elif user_guessed_letter in word_to_guess:
        if user_guessed_letter in word_from_letters_guessed:
            count +=1
            print(f"Already guessed. This was your {count} wrong guess.")
            if count >= 7:
                print(f"You are hanged. This was your {count} wrong guess.")
                break
            continue
        for i in range(0,len(word_to_guess)):
            if word_from_letters_guessed[i] == "_":
                word_from_letters_guessed[i] = user_guessed_letter
                print(word_from_letters_guessed)
                # This shows each letter and number of its occurences in "word_from_letters_guessed".
                print(f"Letter correct, {user_guessed_letter}. This was your {count} guess.")    
                break
    wtg = set(word_to_guess)
    wflg = set(word_from_letters_guessed)
    if wtg == wflg:
        print(f"You have found the word to guess: {''.join(word_to_guess)}. And you needed {count} wrong guesses.")
        break
    elif count >= 7:
        break
print()


# Second Code Example
print("Second way")
print()
# There is a shotcut. We will consider each letter as unique.

# Open, read file and choose random word from file.
with open("sowpods.txt", "r") as open_file:
        text = open_file.read()
        words = text.split()
        word = random.choice(words)
        print(word)
        # Split word to letters.
        letters = []
        for i in word:
             letters.append(i)
        print(letters)
        set_letters = set(letters)
        set_letters = sorted(set_letters)
        print(set_letters)
        
# Compare word from file with user´s guess.
count = 0
hangman = []
while True:
    # User should guess LETTERS from that random word from file.
    print("Welcome to Hangman´s game.")
    user_letter_guess = input("Guess the LETTER from Hangman´s word: ")
    print(user_letter_guess)

    if user_letter_guess not in string.ascii_uppercase:   
        count +=1
        print(f"Letter incorrect, or not in uppercase. This was your {count} wrong guess.")
        if count >= 7:
            print(f"You are hanged. This was your {count} wrong guess.")
            break
        continue
    elif user_letter_guess not in set_letters:
        count +=1
        print(f"Wrong guess. This was your {count} wrong guess.")
        if count >= 7:
            print(f"You are hanged. This was your {count} wrong guess.")
            break
        continue
    elif user_letter_guess in set_letters:
        if user_letter_guess in hangman:
            count +=1
            print(f"Already guessed. This was your {count} wrong guess.")
            if count >= 7:
                print(f"You are hanged. This was your {count} wrong guess.")
                break
        elif user_letter_guess not in hangman:
            hangman.append(user_letter_guess)
            print(hangman)
            print(f"Letter correct, {user_letter_guess}. This was your {count} wrong guess.")
            if len(set_letters) == len(hangman):
                print(word)
                print(f"You have found the word: {word}. And you needed {count} guess.")
                break