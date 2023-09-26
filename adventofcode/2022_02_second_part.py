#2 Following the Elf's instructions for the second column, what would your total score be if everything goes exactly according to your strategy guide?

import collections


with open("2022_02.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))
    # This is my opponent (A, B, C).
    my_opponent = []
    # This is me (X, Y, Z).
    my_moves = []
    for i in range(0,len(lines)):
        opponent = lines[i][0:1]
        my_opponent.append(opponent)
        me = lines[i][2:3]
        my_moves.append(me)
    # This is my opponent (A, B, C).
    print(my_opponent)  
    # This is me (X, Y, Z).
    print(my_moves)


    # X     Loss    0 points
    # Y     Draw    3 points
    # Z     Win     6 points
    my_moves_nextlist= my_moves.copy()
    for i in range(0, len(my_moves_nextlist)):
        if my_moves_nextlist[i] == 'X':
            my_moves_nextlist[i] = 0
        if my_moves_nextlist[i] == 'Y':
            my_moves_nextlist[i] = 3
        if my_moves_nextlist[i] == 'Z':
            my_moves_nextlist[i] = 6
    print(my_moves_nextlist)
## These are points for my losses, draws and wins.
    print("First part of results.")
    first_results = int(sum(my_moves_nextlist))
    print(first_results)
    print(f"These are points for my losses, draws and wins: {first_results}.")
    print()


    # A     Rock        1 points
    # B     Paper       2 points
    # C     Scissors    3 points
    # X     Rock        1 points
    # Y     Paper       2 points
    # Z     Scissors    3 points
    my_opponent = my_opponent.copy()
    print(my_opponent)
    my_moves_change = my_moves.copy()
    print(my_moves_change)
    for i in range(0, len(my_moves_change)):
        for i in range(0, len(my_opponent)):
            # I should loose.
            if my_moves_change[i] == 'X' and my_opponent[i] == 'A':  
                my_moves_change[i] = 'C'
            elif my_moves_change[i] == 'X' and my_opponent[i] == 'B':  
                my_moves_change[i] = 'A'
            elif my_moves_change[i] == 'X' and my_opponent[i] == 'C':  
                my_moves_change[i] = 'B'
            # I should draw.
            elif my_moves_change[i] == 'Y' and my_opponent[i] == 'A':  
                my_moves_change[i] = 'A'
            elif my_moves_change[i] == 'Y' and my_opponent[i] == 'B':  
                my_moves_change[i] = 'B'
            elif my_moves_change[i] == 'Y' and my_opponent[i] == 'C':  
                my_moves_change[i] = 'C'
            # I should win.
            elif my_moves_change[i] == 'Z' and my_opponent[i] == 'A':  
                my_moves_change[i] = 'B'
            elif my_moves_change[i] == 'Z' and my_opponent[i] == 'B':  
                my_moves_change[i] = 'C'
            elif my_moves_change[i] == 'Z' and my_opponent[i] == 'C':  
                my_moves_change[i] = 'A'
    print(my_moves_change)
    for i in range(0, len(my_moves_change)):
        if my_moves_change[i] == 'A':
            my_moves_change[i] = 1
        elif my_moves_change[i] == 'B':
            my_moves_change[i] = 2
        elif my_moves_change[i] == 'C':
            my_moves_change[i] = 3
    print(my_moves_change)
## This is sum of points just for my moves.
    print("Second part of results.")
    second_results = int(sum(my_moves_change))
    print(second_results)
    print(f"This is sum of points (just for moves) for me: {second_results}.")
    print() 


### RESULT
    print(f"Result is: {first_results+second_results}.")