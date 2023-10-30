#1 Simulate your complete hypothetical series of motions. How many positions does the tail of the rope visit at least once?


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


with open("2022_09.txt", "r") as open_file:
    
    # Read file as "dictionary".
    my_dict = {}
    for line in open_file:
        x = line.split()
        my_dict.update({x[0].strip() : x[1].strip()})
    #print(my_dict)
    # These are moves of the letters one by one.
    for key in my_dict:
        if key == "R":
            print("You have to move RIGHT " + my_dict[key] + " steps.")
        elif key == "L":
            print("You have to move LEFT " + my_dict[key] + " steps.")
        elif key == "D":
            print("You have to move DOWN " + my_dict[key] + " steps.")
        else:
            print("You have to move UP " + my_dict[key] + " steps.")
    print()
    

    my_list = [
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.'],
    ['H', '.', '.', '.', '.', '.']
    ]
    for item in my_list:
        print(item)
    print()


    # Iterate over each row.
    for i in range(len(my_list)):
        # Iterate over each column.
        for j in range(len(my_list[i])):
            # Check if the current element is equal to "H".
            if my_list[i][j] == 'H':
                # Print the position of "H".
                print(f"Found 'H' at position ({i},{j}).")
                # Print new index and new position of "H".
                h_row = my_list[i]
                print(h_row)
                h_column_index = h_row.index('H')
                print(h_column_index)
                h_column_index_new = h_column_index + 4
                print(h_column_index_new)
                my_list[i][j] = '.'
                my_list[i][h_column_index_new] = 'H'
                print(h_row)
                break