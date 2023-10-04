#1 After the rearrangement procedure completes, what crate ends up on top of each stack?

# LISTS ALL INSTALLED LIBRARIES
#   pip list


with open("2022_05.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))

    print()
    list_items = []
    for i in range(0,9):
        item = lines[i].strip()
        list_items.append(item)
    print(list_items)

    print()
    print("This prints the positions of crates.")
    for i in list_items:
        print(i, end="\n")

    print()
    print("These are predefined moves with crates.")
    list_items_steps = []
    for i in range(10,len(lines)):
        item = lines[i].strip()
        list_items_steps.append(item)
    print(list_items_steps)
    # This parse each row of predefined moves.
    for i in range(0,len(list_items_steps)):
        number_of_crates_to_move = list_items_steps[i][5:6]
        # print(number_of_crates_to_move)
        move_from_pile = list_items_steps[i][12:13]
        # print(move_from_pile)
        move_to_pile = list_items_steps[i][17:18]
        # print(move_to_pile)
    
    crates_board = ["[N]"," - "," - "," - ","[R]"," - "," - "," - ","[C]",
                    "[T]","[J]"," - "," - ","[S]","[J]"," - "," - ","[N]",
                    "[B]","[Z]"," - ","[H]","[M]","[Z]"," - "," - ","[D]",
                    "[S]","[P]"," - ","[G]","[L]","[H]","[Z]"," - ","[T]",
                    "[Q]","[D]"," - ","[F]","[D]","[V]","[L]","[S]","[M]",
                    "[H]","[F]","[V]","[J]","[C]","[W]","[P]","[W]","[L]",
                    "[G]","[S]","[H]","[Z]","[Z]","[T]","[F]","[V]","[H]",
                    "[R]","[H]","[Y]","[M]","[T]","[M]","[T]","[Q]","[W]",
                    " 1 "," 2 "," 3 "," 4 "," 5 "," 6 "," 7 "," 8 "," 9 "]
    # print(crates_board)

    def print_board():
        print(crates_board[0] + crates_board[1] + crates_board[2] + crates_board[3] + crates_board[4] + crates_board[5] + crates_board[6] + crates_board[7] + crates_board[8]) 
        print(crates_board[9] + crates_board[10] + crates_board[11] + crates_board[12] + crates_board[13] + crates_board[14] + crates_board[15] + crates_board[16] + crates_board[17]) 
        print(crates_board[18] + crates_board[19] + crates_board[20] + crates_board[21] + crates_board[22] + crates_board[23] + crates_board[24] + crates_board[25] + crates_board[26]) 
        print(crates_board[27] + crates_board[28] + crates_board[29] + crates_board[30] + crates_board[31] + crates_board[32] + crates_board[33] + crates_board[34] + crates_board[35]) 
        print(crates_board[36] + crates_board[37] + crates_board[38] + crates_board[39] + crates_board[40] + crates_board[41] + crates_board[42] + crates_board[43] + crates_board[44]) 
        print(crates_board[45] + crates_board[46] + crates_board[47] + crates_board[48] + crates_board[49] + crates_board[50] + crates_board[51] + crates_board[52] + crates_board[53]) 
        print(crates_board[54] + crates_board[55] + crates_board[56] + crates_board[57] + crates_board[58] + crates_board[59] + crates_board[60] + crates_board[61] + crates_board[62]) 
        print(crates_board[63] + crates_board[64] + crates_board[65] + crates_board[66] + crates_board[67] + crates_board[68] + crates_board[69] + crates_board[70] + crates_board[71]) 
        print(crates_board[72] + crates_board[73] + crates_board[74] + crates_board[75] + crates_board[76] + crates_board[77] + crates_board[78] + crates_board[79] + crates_board[80]) 
        return
    
    print()
    print("Board at the begining of predefined moves.")
    print_board()