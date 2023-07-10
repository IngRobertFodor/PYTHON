## Example 1

column = 4
rows = 5

for row in range(0, rows):
    for star in range(0, column):
        print("*", end="")
    print("", end="\n")
# Empty row.
print()


## Example 2

# row_value = Number of stars in each row, row 4 are 4 stars for example.
row_value = 1
rows = 8

for row_value in range(1, rows + 1):
    for star in range(0, row_value):
        print("*", end="")
    print("", end="\n")
for row_value in range(rows - 1, 0, -1):
    for star in range(0, row_value):
        print("*", end="")
    print("", end="\n")
# Empty row.
print()


## Example 3

rows = 5

for row_value in range(1, rows + 1):
    for number in range(1, row_value + 1):
        print(str(number) + " ", end="")    
    print("", end="\n")
for row_value in range(rows - 1, 0, -1):
    for number in range(1, row_value + 1):
        print(str(number) + " ", end="")    
    print("", end="\n")
# Empty row.
print()