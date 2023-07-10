## Example 1

rows = 4
i = 1

while True:
    if i < rows:
        print(i)
        i = i + 1
    if i == rows-2:
        print(i-1, i)
        i = i + 1
    if i == rows-1:
        print(i-2, i-1, i)
        i = i + 1
    if i == rows:
        print(i-3, i-2, i-1, i)
        i = i + 1
    if i > rows:
        print(i-4, i-3 , i-2)
        print(i-4, i-3)
        print(i-4)
        break