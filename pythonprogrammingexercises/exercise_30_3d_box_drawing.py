# 3D Box Drawing

def draw_3d_box(size):
    if type(size)!=int or size<1:
        return print("None")
    
    else:
        
        print(" "*(size+1), "+", (size*2)*"-", "+", sep="")
        
        for i in range(0,size):
            print(" "*(size-i), "/", (size*2)*" ", "/", sep="", end="")
            print(" "*(i), "|", sep="")
      
        print("+", (size*2)*"-", "+", size*" ", "+", sep="")
                
        for j in range(0,size):
            print("|", (size*2)*" ", "|", sep="", end="")
            print(" "*(size-j), "/", sep="")
        
        print("+", (size*2)*"-", "+", sep="")


draw_3d_box(1)
draw_3d_box(2)
draw_3d_box(3)
draw_3d_box(4)
draw_3d_box(5)
print()
draw_3d_box(0)