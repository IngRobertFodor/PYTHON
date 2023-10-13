#1 Find all of the directories with a total size of at most 100000. What is the sum of the total sizes of those directories?

import sys
from collections import defaultdict


with open("2022_07.txt", "r") as open_file:
    
    # We read the file here.
    # (Some "print()"s are hidden, because output is not readable with all prints active.).
    print()
    lines = open_file.readlines()
    print("We read the raw file here.")
    print(lines)
    print()
    list_items = []
    print("We read the file here.")
    for i in range(0,len(lines)):
        line = lines[i].strip().split()
        list_items.append(line)
        print(line)
    print(list_items)
    print()

        # We list all directories now.
    print("     We list all directories now.")
    print()
        # 1. Highest Level:
        # cd /
    x = list_items[0]
    print("     Highest level is: " + str(x) + ".")
    print()

        # 2. Second Level:
        # directories and files under cd /
    character_one = "$ cd"
    xx = []
    for i in range(1,len(list_items)):
        xx.append(list_items[i])
   
    print("     Directories and files under: 'cd /':")
    print(xx)
    print()