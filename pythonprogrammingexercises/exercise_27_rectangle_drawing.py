# Rectangle Drawing

def draw_rectangle(width,height):
    if type(height)!=int or height<=0 or type(width)!=int or width<=0:
        return print("None")
    else:
        for row in range(0,height):
            for column in range(0,width):
                print("#", end="")
            print()
        return


draw_rectangle(10,4)
print()
draw_rectangle(-10,4)
draw_rectangle(10,-4)
draw_rectangle(10,0)
draw_rectangle(0,10)