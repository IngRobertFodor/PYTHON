#1 Simulate your complete hypothetical series of motions. How many positions does the tail of the rope visit at least once?

'''
# Training
#########################################################################################
result_one = []
result_two = []
list_aaaaa = ["Test_a","Test_aa","Test_bb","Test_aaa","Test_aaaa"]
list_bbbbb = ["Test_b","Test_bb","Test_bbb","Test_bbbb","Test_aa"]
list_ccccc = ["Test_c","Test_cc","Test_aa","Test_ccc","Test_cccc"]
for i in list_aaaaa:
    for j in list_bbbbb:
        if i == j:
            result_one.append(i)
            for k in list_ccccc:
                if i == k:
                    result_two.append(i)
print(result_one)
print(result_two)
print()
#########################################################################################
'''

my_list = [
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.']
    ]
start = "#"
my_list[4][0] = start
for item in my_list:
    print(item)
print()

t_movement_row = 4
t_movement_column =  0
h_movement_row = 4
h_movement_column =  0
tail_place = "T"
head_place = "H"
dot_place = "."

my_dictionary = {"my_direction": "", "steps": ""}


with open("UNFINISHED_2022_09.txt", "r") as open_file:  

    lines = open_file.readlines()
    #print(lines)
    #print()

    for line in lines:
        strip_line = line.strip()
        #print(strip_line)  
        my_dictionary["my_direction"] = strip_line[0:1]
        my_dictionary["steps"] = strip_line[2:]
        print(my_dictionary)
        
        if my_dictionary["my_direction"] == "R":
            print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list[h_movement_row][h_movement_column] = dot_place
                h_movement_column = h_movement_column + 1
                print("h moves:",h_movement_row,h_movement_column)
                my_list[h_movement_row][h_movement_column] = head_place
                my_list[t_movement_row][t_movement_column] = tail_place
                for item in my_list:
                    print(item)
                # Tail Moves
                # Tail Moves
                my_list[t_movement_row][t_movement_column] = tail_place
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and h_movement_column-t_movement_column==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row
                    t_movement_column = h_movement_column - 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
                elif h_movement_column-t_movement_column==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column - 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)    
            print()
            print("Result List:",t_movement_row,t_movement_column)
            print()

        ### This should have all conditions implemented (It should be similar in all directions).        
        elif my_dictionary["my_direction"] == "U":
            print(h_movement_row,h_movement_column)
            ## Head Moves
            # This is the "H" movement.
            for move in range(0,int(my_dictionary["steps"])):
                my_list[h_movement_row][h_movement_column] = dot_place
                h_movement_row = h_movement_row - 1
                print("h moves:",h_movement_row,h_movement_column)
                my_list[h_movement_row][h_movement_column] = head_place
                for item in my_list:
                    print(item)
                ## Tail Moves
                # This alligns rows and columns for "H" and "T".
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and t_movement_row-h_movement_row==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column
                    t_movement_row = h_movement_row + 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
                # This will continue in following the "H" with "T".
                elif t_movement_row-h_movement_row==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row + 1
                    my_list[t_movement_row][t_movement_column] = tail_place
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
            print()
            print("Result List:",t_movement_row,t_movement_column)
            print()

        elif my_dictionary["my_direction"] == "L":
            print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list[h_movement_row][h_movement_column] = dot_place
                h_movement_column = h_movement_column - 1
                print("h moves:",h_movement_row,h_movement_column)
                my_list[h_movement_row][h_movement_column] = head_place
                for item in my_list:
                    print(item)
                # Tail Moves
                my_list[t_movement_row][t_movement_column] = tail_place
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and t_movement_column-h_movement_column==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row
                    t_movement_column = h_movement_column + 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
                elif t_movement_column-h_movement_column==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column + 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
            print()
            print("Result List:",t_movement_row,t_movement_column)
            print()

        elif my_dictionary["my_direction"] == "D":
            print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list[h_movement_row][h_movement_column] = dot_place
                h_movement_row = h_movement_row + 1
                print("h moves:",h_movement_row,h_movement_column)
                my_list[h_movement_row][h_movement_column] = head_place
                for item in my_list:
                    print(item)
                # Tail Moves
                my_list[t_movement_row][t_movement_column] = tail_place
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and h_movement_row-t_movement_row==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column
                    t_movement_row = h_movement_row - 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
                elif h_movement_row-t_movement_row==2:
                    my_list[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row - 1
                    print("t moves:",t_movement_row,t_movement_column)
                    my_list[t_movement_row][t_movement_column] = tail_place
                    for item in my_list:
                        print(item)
            print()
            print("Result List:",t_movement_row,t_movement_column)
            print()