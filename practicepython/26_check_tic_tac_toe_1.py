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


# Tic-Tac-Toe Game

# Tic-Tac-Toe - Step 1
# Game board (Different from Script - 024_draw_game_board.py).

winner = ""
playing = True
board = [" - "," - "," - ",
         " - "," - "," - ",
         " - "," - "," - "]

def print_board():
    print("-----------")
    print(board[0] + "|" + board[1] +  "|" + board[2])
    print("-----------")
    print(board[3] + "|" + board[4] +  "|" + board[5])
    print("-----------")
    print(board[6] + "|" + board[7] +  "|" + board[8])
    print("-----------")
    return

# Tic-Tac-Toe - Step 2
# Game inputs.

current_player = " X "  

def game_inputs():
    player_input = int(input("Enter number from 1-9: "))
    while True:
        if player_input >=1 and player_input <=9 and board[player_input-1] == " - ":
            board[player_input-1] = current_player
            print_board()
        # board[player_input-1] != " - "
        else:
            print("Game is full.")
        return

# Tic-Tac-Toe - Step 3
# Switching players and game inputs.

second_player = " O "

def switch_players():
    player_two_input = int(input("Enter number from 1-9: "))
    while True:
        if player_two_input >=1 and player_two_input <=9 and board[player_two_input-1] == " - ":
            board[player_two_input-1] = second_player
            print_board()
        # board[player_input-1] != " - "
        else:
            print("Game is full.")
        return

# Tic-Tac-Toe - Step 4
# User wins or it is a tie.

# board[0] == board[1] == board[2] and board[0] != " - "
    # This means that these values are same (board[0] == board[1] == board[2]). It can be "X" or "O".
    # Not that these values are same " - " == " - " == " - ".
def horizontal_win():
    global winner
    if board[0] == board[1] == board[2] and board[0] != " - ":
        winner = board[0]
    elif board[3] == board[4] == board[5] and board[3] != " - ":
        winner = board[3]
    elif board[6] == board[7] == board[8] and board[6] != " - ":
        winner = board[6]
    return winner

def vertical_win():
    global winner
    if board[0] == board[3] == board[6] and board[0] != " - ":
        winner = board[0]
    elif board[1] == board[4] == board[7] and board[1] != " - ":
        winner = board[1]
    elif board[2] == board[5] == board[8] and board[2] != " - ":
        winner = board[2]
    return winner

def diagonal_win():
    global winner
    if board[0] == board[4] == board[8] and board[0] != " - ":
        winner = board[0]
    elif board[2] == board[4] == board[6] and board[2] != " - ":
        winner = board[2]
    return winner

def finalizing():    
    global winner
    global playing
    while playing: 
        horizontal_win()
        vertical_win()
        diagonal_win()
        if winner  != "":
            # The winner is the one who first joins three same symbols.
            print(f"The winner is {winner}.")
            playing = False
        return


if __name__ == "__main__":

    print_board()
    while True:
        game_inputs()
        switch_players()
        finalizing()