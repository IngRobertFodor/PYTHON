# Multiplication Table

for row in range(1,11):
    for column in range(1,11):
        xy = row*column
        xy = str(xy)
        print(xy.rjust(2), " ", end="")
    print()