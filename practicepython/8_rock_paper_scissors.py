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
# SEARCH PURPOSES (RegEx)
import re
# DELETE, FILE HANDLING PURPOSES
import os
# MATPLOTLIB, VISUALIZATION PURPOSES
import matplotlib
# MYSQL PURPOSES
import mysql.connector


# This is just for fun random game move selection.
game_moves = ("rock","paper","scissors")
random_game_move = random.choice(game_moves)
print(random_game_move)


# These are game moves for two players.
player_one = input("Give me Your game move: ")
player_one = str(player_one)
print("Player One: Your game move was " + player_one + ".")
player_two = input("Give me Your game move: ")
print("Player Two: Your game move was", player_two,".")
player_two = str(player_two)


if (player_one == "paper" and player_two == "rock"):
    print("Player 1 wins.")
elif (player_one == "paper" and player_two == "scissors"):
    print("Player 2 wins.")
elif (player_one == "rock" and player_two == "paper"):
    print("Player 2 wins.")
elif (player_one == "rock" and player_two == "scissors"):
    print("Player 1 wins.")
elif (player_one == "scissors" and player_two == "paper"):
    print("Player 1 wins.")
elif (player_one == "scissors" and player_two == "rock"):
    print("Player 2 wins.")
# These options below are duplicite, all have been mentioned in elifs above.
# elif (player_two == "paper" and player_one == "rock"):
#     print("Player 1 wins.")
# elif (player_two == "paper" and player_one == "scissors"):
#     print("Player 2 wins.")
# elif (player_two == "rock" and player_one == "paper"):
#     print("Player 2 wins.")
# elif (player_two == "rock" and player_one == "scissors"):
#     print("Player 1 wins.")
# elif (player_two == "scissors" and player_one == "paper"):
#     print("Player 1 wins.")
# elif (player_two == "scissors" and player_one == "rock"):
#     print("Player 2 wins.")
else:
    print("Do you want Rematch?")