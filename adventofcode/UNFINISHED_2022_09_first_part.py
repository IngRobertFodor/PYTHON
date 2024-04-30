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
start = "s"
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
            my_list[h_movement_row][h_movement_column] = dot_place
            h_movement_column = h_movement_column + int(my_dictionary["steps"])
            print(h_movement_row,h_movement_column)
            my_list[h_movement_row][h_movement_column] = head_place
            for item in my_list:
                print(item)
            # Tail Moves
            my_list[t_movement_row][t_movement_column] = dot_place
            t_movement_column = t_movement_column + int(my_dictionary["steps"])
            print(t_movement_row,t_movement_column)
            my_list[t_movement_row][t_movement_column] = tail_place
            for item in my_list:
                print(item)
            print()

        elif my_dictionary["my_direction"] == "U":
            print(h_movement_row,h_movement_column)
            # Head Moves
            my_list[h_movement_row][h_movement_column] = dot_place           
            h_movement_row = h_movement_row - int(my_dictionary["steps"])
            print(h_movement_row,h_movement_column)
            my_list[h_movement_row][h_movement_column] = head_place
            for item in my_list:
                print(item)
            # Tail Moves
            my_list[t_movement_row][t_movement_column] = dot_place
            t_movement_row = t_movement_row - int(my_dictionary["steps"])
            print(t_movement_row,t_movement_column)
            my_list[t_movement_row][t_movement_column] = tail_place
            for item in my_list:
                print(item)
            print()

        elif my_dictionary["my_direction"] == "L":
            print(h_movement_row,h_movement_column)
            # Head Moves
            my_list[h_movement_row][h_movement_column] = dot_place           
            h_movement_column = h_movement_column - int(my_dictionary["steps"])
            print(h_movement_row,h_movement_column)
            my_list[h_movement_row][h_movement_column] = head_place
            for item in my_list:
                print(item)
            # Tail Moves
            my_list[t_movement_row][t_movement_column] = dot_place
            t_movement_column = t_movement_column - int(my_dictionary["steps"])
            print(t_movement_row,t_movement_column)
            my_list[t_movement_row][t_movement_column] = tail_place
            for item in my_list:
                print(item)
            print()

        elif my_dictionary["my_direction"] == "D":
            print(h_movement_row,h_movement_column)
            # Head Moves
            my_list[h_movement_row][h_movement_column] = dot_place           
            h_movement_row = h_movement_row + int(my_dictionary["steps"])
            print(h_movement_row,h_movement_column)
            my_list[h_movement_row][h_movement_column] = head_place
            for item in my_list:
                print(item)
            # Tail Moves
            my_list[t_movement_row][t_movement_column] = dot_place
            t_movement_row = t_movement_row + int(my_dictionary["steps"])
            print(t_movement_row,t_movement_column)
            my_list[t_movement_row][t_movement_column] = tail_place
            for item in my_list:
                print(item)
            print()