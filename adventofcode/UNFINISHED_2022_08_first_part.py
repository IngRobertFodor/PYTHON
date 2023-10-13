#1 Consider your map; how many trees are visible from outside the grid?


with open("2022_08.txt", "r") as open_file:

    lines_list = []
    lines = open_file.readlines()
    for i in range(0,len(lines)):
        lines_list.append(lines[i])
    print(lines_list)
    print()
    
    for i in range(0,len(lines_list)):
        lines_list[i] = lines_list[i].strip()
        print(lines_list)
    print()

    for i in range(0,len(lines_list)):
        print(lines_list[i])
    print()

    for i in range(0,len(lines_list)):
        print(list(lines_list[i]))
    print()