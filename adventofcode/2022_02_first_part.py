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
    
    # These will be base data to calculate sum for loses, draws or wins (0, 3, 6).
    for i in range(0,len(my_opponent)):
        if my_opponent[i] == "A":
            my_opponent[i] = "1"
        elif my_opponent[i] == "B":
            my_opponent[i] = "2"
        elif my_opponent[i] == "C":
            my_opponent[i] = "3"
    print(my_opponent)
    print(len(my_opponent))
    for j in range(0,len(my_moves)):
        if my_moves[j] == "X":
            my_moves[j] = "1"
        elif my_moves[j] == "Y":
            my_moves[j] = "2"
        elif my_moves[j] == "Z":
            my_moves[j] = "3"
    print(my_moves)
    print(len(my_moves))

    # This will be sum for draws. 
    my_opponent_draws = my_opponent.copy()
    my_moves_draws = my_moves.copy()
    for i in range(0, len(my_opponent_draws)):
        for i in range(0, len(my_moves_draws)):
            if my_opponent_draws[i] == my_moves_draws[i]:
                my_opponent_draws[i] = "draw"  
                my_moves_draws[i] = "draw"       
    print(my_opponent_draws)
    print(my_moves_draws)
    results_draws = []
    for item in my_opponent_draws:
        if item == "draw":
            results_draws.append(item)
    print(results_draws)
    print(len(results_draws))
## These are points for draws.
    print("Second part of results.")
    draw_points = len(results_draws) * 3
    print(f"For draw are same points for my opponent and me: {draw_points}.")
    print()

    # This will be sum for my wins. 
    my_opponent_nextlist = my_opponent_draws.copy()
    my_moves_nextlist = my_moves_draws.copy()
    for i in range(0, len(my_opponent_nextlist)):
        for i in range(0, len(my_moves_nextlist)):
            if my_opponent_nextlist[i] == '3' and my_moves_nextlist[i] == '1':
                my_opponent_nextlist[i] = "loss"  
                my_moves_nextlist[i] = "win"
            elif my_opponent_nextlist[i] == '1' and my_moves_nextlist[i] == '2':
                my_opponent_nextlist[i] = "loss"  
                my_moves_nextlist[i] = "win"
            elif my_opponent_nextlist[i] == '2' and my_moves_nextlist[i] == '3':
                my_opponent_nextlist[i] = "loss"  
                my_moves_nextlist[i] = "win"
    print(my_opponent_nextlist)
    print(my_moves_nextlist)    
    results_my_wins = []
    for item in my_moves_nextlist:
        if item == "win":
            results_my_wins.append(item)
    print(results_my_wins)
    print(len(results_my_wins))
## These are points for my wins.
    print("Third part of results.")
    my_win_points = len(results_my_wins) * 6
    print(f"These are my win points: {my_win_points}.")
    print()


### RESULT
    print(f"Result is: {x+y+z+draw_points+my_win_points}")