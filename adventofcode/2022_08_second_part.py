#2 Consider each tree on your map. What is the highest scenic score possible for any tree?


def process_input(input):
    result = 0
    for i, row in enumerate(input):
        for j, _ in enumerate(row):
            tree_index = process_trees(i, j, input, len(input))
            if tree_index > result:
                result = tree_index
            else:
                result += 0
    return result

def process_trees(row, column, input, max_size):
    directions = ["r", "l", "u", "d"]
    result = 1
    for i in range(1, max_size):
        tmp_directions = directions.copy()
        for direction in tmp_directions:
            if direction == "r":
                if column + i == max_size:
                    result *= (i - 1)
                    directions.remove(direction)
                elif input[row][column] <= input[row][column + i]:
                    result *= i
                    directions.remove(direction)
            if direction == "l":
                if column - i < 0:
                    result *= (i - 1)
                    directions.remove(direction)
                elif input[row][column] <= input[row][column - i]:
                    result *= i
                    directions.remove(direction)
            if direction == "d":
                if row + i == max_size:
                    result *= (i - 1)
                    directions.remove(direction)
                elif input[row][column] <= input[row + i][column]:
                    result *= i
                    directions.remove(direction)
            if direction == "u":
                if row - i < 0:
                    result *= (i - 1)
                    directions.remove(direction)
                elif input[row][column] <= input[row - i][column]:
                    result *= i
                    directions.remove(direction)
        if len(directions) == 0:
            break
    return result

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
    print("This is the highest scenic score.")
    print(process_input(input))