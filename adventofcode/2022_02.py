import collections


with open("2022_02.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))
    # This is my opponent (A, B, C).
    keys_list = []
    # This is me (X, Y, Z).
    values_list = []
    
    for i in range(0,len(lines)):
        keys = lines[i][0:1]
        keys_list.append(keys)
        values = lines[i][2:3]
        values_list.append(values)
    # This is my opponent (A, B, C).
    print(keys_list)
    print(collections.Counter(keys_list))
    # This is me (X, Y, Z).
    print(values_list)
    print(collections.Counter(values_list))

    # This counts moves of each player.
    # This is my opponent (A, B, C).
    a = keys_list.count("A")
    print(a)
    a = a*1
    print(a)
    b = keys_list.count("B")
    print(b)
    b = b*2
    print(b)
    c = keys_list.count("C")
    print(c)
    c = c*3
    print(c)
    # This is me (X, Y, Z).
    x = values_list.count("X")
    print(x)
    x = x*1
    print(x)
    y = values_list.count("Y")
    print(y)
    y = y*2
    print(y)
    z = values_list.count("Z")
    print(z)
    z = z*3
    print(z)

    print(f"This is sum (just for moves) for my opponent: {a+b+c}.")
    print(f"This is sum (just for moves) for me: {x+y+z}.")