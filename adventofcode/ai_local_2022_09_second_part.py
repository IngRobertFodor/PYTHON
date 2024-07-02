#1
# create virtual list
# print output, with no newline characters, and "." for empty steps
snake_list = []
for i in range(400):
    i='.'
    snake_list.append(i)
snake_list_chunked = []
chunk_size = 20
for i in range(0, len(snake_list), chunk_size):
    snake_list_chunked.append(snake_list[i:i+chunk_size])
# print virtual list
#for i in snake_list_chunked:
#    print(i)
#print()
# starting position of the snake is "S", at position [5][0]
# snake´s head is "H"
# print virtual list with starting position of the snake
row_snake = 5
column_snake = 0
snake_list_chunked[row_snake][column_snake] = "S"
for i in snake_list_chunked:
    print(i)
print()

#2
# read "local_2022_09.txt" file line by line
# data are in this format: "L 1", "R 2", "U 3", "D 4"
# letter represents directions, number represents number of steps to move
# store data in dictionary in key-value pairs, dict. name - "my_dictionary"
# create empty dictionary
my_dictionary = {}
# open file in read mode
with open("local_2022_09.txt", "r") as file:
    # read file line by line
    for line in file:
        # remove new line character
        line = line.strip()
        # store data in dictionary
        my_dictionary["my_direction"] = line[0:1]
        my_dictionary["steps"] = line[2:]
        # print dictionary
        print(my_dictionary)

        #3
        # use my_dictionary to move the virtual snake in the game (in virtual list)
        # move snake´s head "H" first, head movement starts at positions [row_snake][column_snake]
        # when head moves, its new position is replaced by "H" and its previous position is replaced by "."
        # use if, elif and else statements to move the snake
        # if my_dictionary["my_direction"] == "L", move snake left int(my_dictionary["steps"]) steps 
        # if my_dictionary["my_direction"] == "R", move snake right int(my_dictionary["steps"]) steps
        # if my_dictionary["my_direction"] == "U", move snake up int(my_dictionary["steps"]) steps
        # if my_dictionary["my_direction"] == "D", move snake down int(my_dictionary["steps"]) steps
        # every next move is conneted to the previous move, last position of the snake is the new starting position from which the snake moves
        # move snake
        for i in range(int(my_dictionary["steps"])):
            if my_dictionary["my_direction"] == "L":
                snake_list_chunked[row_snake][column_snake] = "."
                column_snake -= 1
                snake_list_chunked[row_snake][column_snake] = "H"
            elif my_dictionary["my_direction"] == "R":
                snake_list_chunked[row_snake][column_snake] = "."
                column_snake += 1
                snake_list_chunked[row_snake][column_snake] = "H"
            elif my_dictionary["my_direction"] == "U":
                snake_list_chunked[row_snake][column_snake] = "."
                row_snake -= 1
                snake_list_chunked[row_snake][column_snake] = "H"
            elif my_dictionary["my_direction"] == "D":
                snake_list_chunked[row_snake][column_snake] = "."
                row_snake += 1
                snake_list_chunked[row_snake][column_snake] = "H"
        for i in snake_list_chunked:
            print(i)