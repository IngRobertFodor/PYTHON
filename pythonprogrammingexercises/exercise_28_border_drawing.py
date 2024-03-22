# Border Drawing

def draw_border(width, height):
    if type(height)!=int or height<=2 or type(width)!=int or width<=2:
        return print("None")
    else:
        print("+", (width-2) * "-", "+")
        for n in range(0,height-2):
            print("|", (width-2) * " ", "|")
        print("+", (width-2) * "-", "+")


draw_border(16,4)
print()
draw_border(-10,4)
draw_border(10,-4)
draw_border(10,2)
draw_border(0,10)