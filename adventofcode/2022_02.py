from itertools import groupby

with open("2022_02.txt", "r") as open_file:
    
    lines = open_file.read()
    print(lines)
    keys = lines[0:1]
    print(keys)
    values = lines[2:3]
    print(values)
        
    # Create dictionary "my_dictionary".
    # my_dictionary = {lines[i][0:1]: lines[i][2:3] for i in range(0, len(lines))}
    # print(my_dictionary)