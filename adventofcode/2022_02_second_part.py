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
    print(collections.Counter(my_opponent))
    # This is me (X, Y, Z).
    print(my_moves)
    print(collections.Counter(my_moves))

    # This will count moves of each player.
    # These are my opponent's moves (A, B, C).
    a = my_opponent.count("A")
    print(a)
    a = a*1
    print(a)
    b = my_opponent.count("B")
    print(b)
    b = b*2
    print(b)
    c = my_opponent.count("C")
    print(c)
    c = c*3
    print(c)
    # These are my moves (X, Y, Z).
    x = my_moves.count("X")
    print(x)
    x = x*1
    print(x)
    y = my_moves.count("Y")
    print(y)
    y = y*2
    print(y)
    z = my_moves.count("Z")
    print(z)
    z = z*3
    print(z)

## This is sum (just for moves).
    print("First part of results.")
    print(f"This is sum of points (just for moves) for my opponent: {a+b+c}.")
    print(f"This is sum of points (just for moves) for me: {x+y+z}.")
    print()
    
    # T Pointshese will be base data to calculate sum for loses, draws or wins (0, 3, 6).
    # X     Loss    0 points
    # Y     Draw    3 points
    # Z     Win     6 points
    my_moves_nextlist= my_moves.copy()
    print(my_moves_nextlist)
    for i in range(0, len(my_moves_nextlist)):
        if my_moves_nextlist[i] == 'X':
            my_moves_nextlist[i] = 0
        if my_moves_nextlist[i] == 'Y':
            my_moves_nextlist[i] = 3
        if my_moves_nextlist[i] == 'Z':
            my_moves_nextlist[i] = 6
    print(my_moves_nextlist)

## These are points for my losses, draws and wins.
    print("Second part of results.")
    print(sum(my_moves_nextlist))
    print(f"These are points for my losses, draws and wins: {my_moves_nextlist}.")
    print()

### RESULT
    first_results = x+y+z
    print(first_results)
    second_results = int(sum(my_moves_nextlist))
    print(second_results)
    print(f"Result is: {first_results+second_results}.")