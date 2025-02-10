#Pyramid Drawing

def draw_pyramid(number_of_rows):
    for row in range(1,number_of_rows+1):
        # "." represents free space. I have used it, bacause I wanted the code to be more readable.
        dot = "."
        hashtag = "#"
        print(dot * (number_of_rows-row), end="")
        print(hashtag.rjust(2) * (row), end="")
        print(dot * (number_of_rows-row), end="")
        print()

    
draw_pyramid(8)
print()
draw_pyramid(5)