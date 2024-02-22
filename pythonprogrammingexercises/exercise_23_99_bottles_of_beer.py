# 99 Bottles of Beer

for i in range(99, 0, -1):
    if i in  range(2, 100):
        print(i, "bottles of beer on the wall,")
        print(i, "bottles of beer,")
        print("Take one down,")
        print("Pass it around,")
        print(i-1, "bottles of beer on the wall,")
        print()
    elif i == 1:
        print(i, "bottle of beer on the wall,")
        print(i, "bottle of beer,")
        print("Take one down,")
        print("Pass it around,")
        print("No more bottles of beer on the wall!")