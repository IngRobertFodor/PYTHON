# 3D Box Drawing

def draw_3d_box(size):
    if type(size)!=int or size<1:
        return print("None")
    
    else:
        
        print(" "*(size), "+", ((size)*2)*"-", "+")
        
        for i in range(size,0,-1):
            print(" "*(i-1), "/", ((size)*2)*" ", "/")
        
        print("+", ((size)*2)*"-", "+")
        
        for j in range(0,size):
            print("|", ((size)*2)*" ", "|")
        
        print("+", ((size)*2)*"-", "+")


draw_3d_box(1)
draw_3d_box(2)
draw_3d_box(3)
draw_3d_box(4)
draw_3d_box(5)
print()
draw_3d_box(0)