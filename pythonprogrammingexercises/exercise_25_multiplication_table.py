# Multiplication Table

special_character = "  |"
print(special_character.rjust(2), end="")

top_line = ["1","2","3","4","5","6","7","8","9","10"]
for i in top_line:
    print(i.rjust(2), " ", end="")
print()

print("--+---------------------------------------")

for row in range(1,11):   
    str_row = str(row)
    print(str_row.rjust(2), end="")
    print("|", end="")
    for column in range(1,11):
        xy = row*column
        xy = str(xy)
        print(xy.rjust(2), " ", end="")
    print()