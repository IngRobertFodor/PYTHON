#2 Simulate your complete series of motions on a larger rope with ten knots. How many positions does the tail of the rope visit at least once?


import string


my_list = []
for i in range(400):
    i='.'
    my_list.append(i)
my_list_chunked = []
chunk_size = 20
for i in range(0, len(my_list), chunk_size):
    my_list_chunked.append(my_list[i:i+chunk_size])

start = "s"
my_list_chunked[5][0] = start
#for i in my_list_chunked:
#    print(i)
#print()


my_list_tail_positions = []
for i in range(400):
    i='.'
    my_list_tail_positions.append(i)
my_list_tail_positions_chunked = []
chunk_size = 20
for i in range(0, len(my_list_tail_positions), chunk_size):
    my_list_tail_positions_chunked.append(my_list_tail_positions[i:i+chunk_size])

start = "s"
my_list_tail_positions_chunked[5][0] = start
#for i in my_list_tail_positions_chunked:
#    print(i)
#print()


t_movement_row = 5
t_movement_column = 0
h_movement_row = 5
h_movement_column = 0
head_place = "H"
dot_place = "."


with open("local_2022_09.txt", "r") as open_file:  


    lines = open_file.readlines()


    for line in lines:
        strip_line = line.strip()
        my_dictionary = {"my_direction": "", "steps": ""}
        my_dictionary["my_direction"] = strip_line[0:1]
        my_dictionary["steps"] = strip_line[2:]
        print(my_dictionary)
        
        
        tail_place = int(my_dictionary["steps"])
        print("Tail Place:",tail_place)
        

        if my_dictionary["my_direction"] == "R":
            print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list_chunked[h_movement_row][h_movement_column] = dot_place
                h_movement_column = h_movement_column + 1
                print("h moves:",h_movement_row,h_movement_column)
                my_list_chunked[h_movement_row][h_movement_column] = head_place
                for item in my_list_chunked:
                    print(item)
                # Tail Moves
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and h_movement_column-t_movement_column==2:
                    t_movement_row = h_movement_row
                    t_movement_column = h_movement_column - 1
                    print("t moves:",t_movement_row,t_movement_column)
                    if int(tail_place) > 0:
                        tail_place -= 1
                    if int(tail_place) > 0 and int(tail_place) < 10:
                        my_list_chunked[t_movement_row][t_movement_column] = str(tail_place)
                        my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    for item in my_list_chunked:
                        print(str(item).rjust(3))
                elif h_movement_column-t_movement_column==2:
                    t_movement_column = h_movement_column - 1
                    print("t moves:",t_movement_row,t_movement_column)
                    if int(tail_place) > 0:
                        tail_place -= 1
                    if int(tail_place) > 0 and int(tail_place) < 10:
                        my_list_chunked[t_movement_row][t_movement_column] = str(tail_place)
                        my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    for item in my_list_chunked:
                        print(str(item).rjust(3))
            print("Result List:",t_movement_row,t_movement_column)
            print()

        elif my_dictionary["my_direction"] == "U":
            print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list_chunked[h_movement_row][h_movement_column] = dot_place
                h_movement_row = h_movement_row - 1
                print("h moves:",h_movement_row,h_movement_column)
                my_list_chunked[h_movement_row][h_movement_column] = head_place
                for item in my_list_chunked:
                    print(item)
                # Tail Moves
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and t_movement_row-h_movement_row==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column
                    t_movement_row = h_movement_row + 1
                    print("t moves:",t_movement_row,t_movement_column)
                    if int(tail_place) > 0:
                        tail_place -= 1
                    if int(tail_place) > 0 and int(tail_place) < 10:
                        my_list_chunked[t_movement_row][t_movement_column] = str(tail_place)
                        my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    for item in my_list_chunked:
                        print(str(item).rjust(3))
                elif t_movement_row-h_movement_row==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row + 1
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    print("t moves:",t_movement_row,t_movement_column)
                    if int(tail_place) > 0:
                        tail_place -= 1
                    if int(tail_place) > 0 and int(tail_place) < 10:
                        my_list_chunked[t_movement_row][t_movement_column] = str(tail_place)
                        my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    for item in my_list_chunked:
                        print(str(item).rjust(3))
            print("Result List:",t_movement_row,t_movement_column)
            print()


        for i in my_list_tail_positions_chunked:
            print(i)


'''
with open("local_2022_09.txt", "r") as open_file:  

    lines = open_file.readlines()

    for line in lines:
        strip_line = line.strip()
        my_dictionary["my_direction"] = strip_line[0:1]
        my_dictionary["steps"] = strip_line[2:]
        #print(my_dictionary)
        
        if my_dictionary["my_direction"] == "R":
            #print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list_chunked[h_movement_row][h_movement_column] = dot_place
                h_movement_column = h_movement_column + 1
                #print("h moves:",h_movement_row,h_movement_column)
                my_list_chunked[h_movement_row][h_movement_column] = head_place
                my_list_chunked[t_movement_row][t_movement_column] = tail_place
                #for item in my_list_chunked:
                #    print(item)
                # Tail Moves
                my_list_chunked[t_movement_row][t_movement_column] = tail_place
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and h_movement_column-t_movement_column==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row
                    t_movement_column = h_movement_column - 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
                elif h_movement_column-t_movement_column==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column - 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
            #print("Result List:",t_movement_row,t_movement_column)
            #print()

        elif my_dictionary["my_direction"] == "U":
            #print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list_chunked[h_movement_row][h_movement_column] = dot_place
                h_movement_row = h_movement_row - 1
                #print("h moves:",h_movement_row,h_movement_column)
                my_list_chunked[h_movement_row][h_movement_column] = head_place
                #for item in my_list_chunked:
                #    print(item)
                # Tail Moves
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and t_movement_row-h_movement_row==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column
                    t_movement_row = h_movement_row + 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
                elif t_movement_row-h_movement_row==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row + 1
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
            #print("Result List:",t_movement_row,t_movement_column)
            #print()

        elif my_dictionary["my_direction"] == "L":
            #print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list_chunked[h_movement_row][h_movement_column] = dot_place
                h_movement_column = h_movement_column - 1
                #print("h moves:",h_movement_row,h_movement_column)
                my_list_chunked[h_movement_row][h_movement_column] = head_place
                #for item in my_list_chunked:
                #    print(item)
                # Tail Moves
                my_list_chunked[t_movement_row][t_movement_column] = tail_place
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and t_movement_column-h_movement_column==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row
                    t_movement_column = h_movement_column + 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
                elif t_movement_column-h_movement_column==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column + 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
            #print("Result List:",t_movement_row,t_movement_column)
            #print()

        elif my_dictionary["my_direction"] == "D":
            #print(h_movement_row,h_movement_column)
            # Head Moves
            for move in range(0,int(my_dictionary["steps"])):
                my_list_chunked[h_movement_row][h_movement_column] = dot_place
                h_movement_row = h_movement_row + 1
                #print("h moves:",h_movement_row,h_movement_column)
                my_list_chunked[h_movement_row][h_movement_column] = head_place
                #for item in my_list_chunked:
                #    print(item)
                # Tail Moves
                my_list_chunked[t_movement_row][t_movement_column] = tail_place
                if h_movement_row != t_movement_row and h_movement_column !=t_movement_column and h_movement_row-t_movement_row==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_column = h_movement_column
                    t_movement_row = h_movement_row - 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
                elif h_movement_row-t_movement_row==2:
                    my_list_chunked[t_movement_row][t_movement_column] = dot_place
                    t_movement_row = h_movement_row - 1
                    #print("t moves:",t_movement_row,t_movement_column)
                    my_list_chunked[t_movement_row][t_movement_column] = tail_place
                    my_list_tail_positions_chunked[t_movement_row][t_movement_column] = "#"
                    #for item in my_list_chunked:
                    #    print(item)
            #print("Result List:",t_movement_row,t_movement_column)
            #print()


print("This is result list.")
for i in my_list_tail_positions_chunked:
    print(i)

count = 0
for sub_list in my_list_tail_positions_chunked:
    for i in sub_list:
        if i == "#" or i=="s":
            count += 1
print(count)
'''