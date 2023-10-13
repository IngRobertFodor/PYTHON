#1 Consider your map; how many trees are visible from outside the grid?


with open("UNFINISHED_2022_08.txt", "r") as open_file:

    # Rows
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

    print("Rows") 
    for i in lines_list:
        print(list(i))
    print()
    
    # Rows details
    print("Rows details")
    aa = []
    for i in range(0,len(lines_list)):
        a = list(lines_list[i])
        aa.append(a)
        maxx = max(a)
        print(f'Max value: {maxx}.')
        ind = a.index(str(maxx))
        print(f'Index of max value: {ind}, row: {a}.')      
    print()

    # Columns
    print("Columns")
    lines_columns = zip(*lines_list)
    for i in lines_columns:
        print(list(i))
    print()