#1 Consider your map; how many trees are visible from outside the grid?


with open("2022_08.txt", "r") as open_file:

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
        print(a)
        aa.append(a)
        maxx_row = max(a)
        print(f'Max value in row: {maxx_row}.')
        ind = a.index(str(maxx_row))
        print(f'Index of max row value: {ind}, in row: {a}.')      
    print()

    # Columns
    print("Columns")
    lines_columns = zip(*lines_list)
    for i in lines_columns:
        b = list(i)
        print(b)
    print()
    
    # Columns details
    print("Columns details")
    lines_columns = zip(*lines_list)
    for i in lines_columns:
        b = list(i)
        print(b)
        maxx_column = max(b)
        print(f'Max value in column: {maxx_column}.')
        ind = b.index(str(maxx_column))
        print(f'Index of max column value: {ind}, in column: {b}.')
    print()