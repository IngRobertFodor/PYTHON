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


winner = ""
playing = True
current_player = " X "

board = [" - "," - "," - ",
         " - "," - "," - ",
         " - "," - "," - "]

def print_board(board):
    print("-----------")
    print(board[0] + "|" + board[1] +  "|" + board[2])
    print("-----------")
    print(board[3] + "|" + board[4] +  "|" + board[5])
    print("-----------")
    print(board[6] + "|" + board[7] +  "|" + board[8])
    print("-----------")

def player_input(board):
    inp = int(input("Enter number from 1-9: "))
    while True:
        if inp >=1 and inp <=9 and board[inp-1] == " - ":
            board[inp-1] = current_player
        else:
            print("Player is already in that spot.")
        return
    
def horizontal_win(board):
    global winner
    if board[0] == board[1] == board[2] and board[0] != " - ":
        winner = board[0]
        return True
    elif board[3] == board[4] == board[5] and board[3] != " - ":
        winner = board[3]
        return True
    elif board[6] == board[7] == board[8] and board[6] != " - ":
        winner = board[6]
        return True

def vertical_win(board):
    global winner
    if board[0] == board[3] == board[6] and board[0] != " - ":
        winner = board[0]
        return True
    elif board[1] == board[4] == board[7] and board[1] != " - ":
        winner = board[1]
        return True
    elif board[2] == board[5] == board[8] and board[2] != " - ":
        winner = board[2]
        return True
    
def diagonal_win(board):
    global winner
    if board[0] == board[4] == board[8] and board[0] != " - ":
        winner = board[0]
        return True
    elif board[2] == board[4] == board[6] and board[2] != " - ":
        winner = board[2]
        return True

# Remíza = TIE
def check_tie(board):
    global playing
    if " - " not in board:
        print_board(board)
        print("No free spots on the board.")
        playing = False
    return

def check_for_win(board):
    if horizontal_win(board) or vertical_win(board) or diagonal_win(board):
        print(f"The winner is {winner}.")
    return

def switch_players():
    global current_player
    if current_player == " X ":
        current_player = " O "
    else:
        current_player = " X "
    return


while playing:
    print_board(board)
    player_input(board)
    check_for_win(board)
    check_tie(board)
    switch_players()