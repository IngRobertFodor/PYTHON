#1 Find all of the directories with a total size of at most 100000. What is the sum of the total sizes of those directories?
#2 Find the smallest directory that, if deleted, would free up enough space on the filesystem to run the update. What is the total size of that directory?

from itertools import accumulate


stack = []
sizes = {}

with open("2022_07.txt", "r") as open_file:
    
    for line in open_file:
        
        if line.startswith("$ ls") or line.startswith("dir"):
            continue
        line_split = line.split()
        print(line_split)
        if line.startswith("$ cd") and line_split[2] != (".."):
            stack.append(line_split[2])
        elif line.startswith("$ cd") and line_split[2] == (".."):
            stack.pop()
        else:
            for folder in accumulate(stack, lambda x,y: x + "*" + y):
                if folder not in sizes.keys():
                    sizes[folder] = 0
                sizes[folder] += int(line_split[0])
    
    print()
    print(sizes.keys())
    print(sizes.values())
    
    #1 Find all of the directories with a total size of at most 100000. What is the sum of the total sizes of those directories?
    print(sum(filter(lambda v: v < 100000, sizes.values())))
    
    print()
    print("From 70 000 000 available on disk is used: " + str(sizes["/"]) + ". And we need 30 000 000 to be free on disk.")
    #2 Find the smallest directory that, if deleted, would free up enough space on the filesystem to run the update. What is the total size of that directory?
    print("This is folder to delete:")
    print(min(filter(lambda v: sizes["/"] - 40000000 <= v, sizes.values())))