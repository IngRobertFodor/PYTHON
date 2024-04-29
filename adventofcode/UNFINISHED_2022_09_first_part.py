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
for item in my_list:
    print(item)
print()


movement_row = 4
movement_column =  0

tail_place = my_list[movement_row][movement_column]
tail_place = "T"
print(tail_place)
print("Tail place:",tail_place,"starting position is: my_list[4][0]")

head_place = my_list[movement_row][movement_column]
head_place = "H"
print(head_place)
print("Head place:",head_place,"starting position is: my_list[4][0]")

my_list = [
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    [head_place, '.', '.', '.', '.', '.']
    ]
for item in my_list:
    print(item)
print()


my_dictionary = {"my_direction": "", "steps": ""}
#print(my_dictionary)
#print()


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
            print(movement_row,movement_column)
            # Head Moves
            my_list[movement_row][movement_column] = "."
            movement_column_head = movement_column + int(my_dictionary["steps"])
            print(movement_row,movement_column_head)
            my_list[movement_row][movement_column_head] = head_place
            # Tail Moves
            movement_column_tail = movement_column + (int(my_dictionary["steps"])-1)
            print(movement_row,movement_column_tail)
            my_list[movement_row][movement_column_tail] = tail_place
            for item in my_list:
                print(item)
            print()




        elif my_dictionary["my_direction"] == "U":
            print(movement_row,movement_column)
            head_place = "."
            movement_row = movement_row - int(my_dictionary["steps"])
            print(movement_row,movement_column)
            my_list[movement_row][movement_column] = head_place
            #
            movement_row_tail = movement_row - (int(my_dictionary["steps"])-1)
            print(movement_row,movement_column)
            my_list[movement_row][movement_column] = tail_place
            for item in my_list:
                print(item)
            print()




        elif my_dictionary["my_direction"] == "L":
            print(movement_row,movement_column)
            my_list[movement_row][movement_column] = "."
            movement_column = movement_column - int(my_dictionary["steps"])
            print(movement_row,movement_column)
            my_list[movement_row][movement_column] = head_place
            for item in my_list:
                print(item)
            print()
    
        elif my_dictionary["my_direction"] == "D":
            print(movement_row,movement_column)
            my_list[movement_row][movement_column] = "."
            movement_row = movement_row + int(my_dictionary["steps"])
            print(movement_row,movement_column)
            my_list[movement_row][movement_column] = head_place
            for item in my_list:
                print(item)
            print()