#1 Find the Elf carrying the most Calories. How many total Calories is that Elf carrying?
#2 Find the top three Elves carrying the most Calories. How many Calories are those Elves carrying in total?

from itertools import groupby


with open("2022_01.txt", "r") as open_file:
   
    lists = [list(g) for k, g in groupby(map(str.strip, open_file), key=lambda line: line != '') if k]
    print(lists)
    print(len(lists))
    results = []
    for i in range(0,len(lists)):
        lists[i] = map(int, lists[i])
        x = sum(lists[i])
        print(x)
        results.append(x)
        results.sort()
    print(results)
    print(results[-1:]) 
        
    next_results = results[-3:]
    print(next_results)
    print(sum(next_results))