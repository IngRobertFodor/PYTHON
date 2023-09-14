with open("2022_02.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))
    keys_list = []
    values_list = []
    for i in range(0,len(lines)):
        keys = lines[i][0:1]
        keys_list.append(keys)
        values = lines[i][2:3]
        values_list.append(values)
    print(keys_list)
    print(values_list)