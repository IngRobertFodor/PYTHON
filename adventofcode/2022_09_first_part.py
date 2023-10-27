#1 Simulate your complete hypothetical series of motions. How many positions does the tail of the rope visit at least once?


def read_file():
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
    return my_dict


if __name__ == "__main__":
    my_input = read_file()
    print(my_input)
