#1 Consider your map; how many trees are visible from outside the grid?


'''
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
    '''


# enumerate()

# When you use "enumerate()", the function gives you back two loop variables:
#   1.The count of the current iteration
#   2. The value of the item at the current iteration


def process_input(input):
    result = 0
    for i, row in enumerate(input):
        for j, _ in enumerate(row):
            tmp = process_trees(i, j, input, len(input))
            if tmp == True:
                result += 1
            else:
                result += 0
    return result

def process_trees(row, column, input, max_size):
    directions = ["r", "l", "u", "d"]
        # These values "range(1,max_size)" represent steps from my chosen tree, in all direcions (e.g. right or left, 1 represent 1 step).
    for i in range(1,max_size):
        tmp_directions = directions.copy()
        for direction in tmp_directions:
            if direction == "r":
                # In this situation I was able to get to the boarder of tree field.
                if column + i == max_size:
                    return True
                # In this situation I was not able to get to the boarder of tree field (there was/were higher tree/trees).
                elif input[row][column] <= input[row][column + i]:
                    directions.remove(direction)
            if direction == "l":
                # In this situation I was able to get to the boarder of tree field.
                if column - i < 0:
                    return True
                # In this situation I was not able to get to the boarder of tree field (there was/were higher tree/trees).
                elif input[row][column] <= input[row][column - i]:
                    directions.remove(direction)
            if direction == "d":
                # In this situation I was able to get to the boarder of tree field.
                if row + i == max_size:
                    return True
                # In this situation I was not able to get to the boarder of tree field (there was/were higher tree/trees).
                elif input[row][column] <= input[row + i][column]:
                    directions.remove(direction)
            if direction == "u":
                # In this situation I was able to get to the boarder of tree field.
                if row - i < 0:
                    return True
                # In this situation I was not able to get to the boarder of tree field (there was/were higher tree/trees).
                elif input[row][column] <= input[row - i][column]:
                    directions.remove(direction)
        if len(directions) == 0:
            return False
    return False

def read_file(input):
    with open("2022_08.txt", "r") as open_file:

        # Rows
        lines_list = []
        lines = open_file.readlines()
        for i in range(0,len(lines)):
            lines[i] = lines[i].strip("\n")
            lines_list.append(lines[i])
        print(lines_list)
        input = lines_list.copy()
        print(input)
        return input


if __name__ == "__main__":
    input = read_file(input)
    print("This is the number of trees.")
    print(process_input(input))