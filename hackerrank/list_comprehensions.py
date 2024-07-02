import itertools
import random


x = int(input("Enter x: "))
y = int(input("Enter y: "))
z = int(input("Enter z: "))
n = int(input("Enter n: "))
print("x: ", x)
print("y: ", y)
print("z: ", z)
print("n: ", n)
i = random.randrange(0, int(x)+1)
j = random.randrange(0, int(y)+1)
k = random.randrange(0, int(z)+1)
print("i: ", i)
print("j: ", j)
print("k: ", k)
print()

variables = [i, j, k]

combinations = list(itertools.product(variables, repeat=3))
print(combinations)
print()

res_list = []
for combination in combinations:
    combination_list_item = list(combination)
    if combination_list_item not in res_list and sum(combination_list_item) != n:
        res_list.append(combination_list_item)
print(res_list)
print()
print("Sorted list: ")
sorted_list = sorted(res_list)
print(sorted_list)