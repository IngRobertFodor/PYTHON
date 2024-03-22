#Pyramid Drawing

def draw_pyramid(number_of_rows):
    for row in range(0,number_of_rows):
        # "." represents free space. I have used it, bacause I wanted the code to be more readable.
        print("."*((number_of_rows-1)-row), end="")
        print("#"*(row), end="")
        print("#", end="")
        print("#"*(row), end="")
        print("."*((number_of_rows-1)-row), end="")
        print()

    
draw_pyramid(8)
print()
draw_pyramid(5)