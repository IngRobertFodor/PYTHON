import numpy as np


### COPY

my_array_one = np.array([1, 2, 3, 4, 5])
print("Original array:", my_array_one)
my_array_copy = my_array_one.copy()
print("Coppied array:", my_array_copy)
print(" I am going to change the first element of the coppied array.")
my_array_copy[0] = 100
print(my_array_one)
print(my_array_copy)
print("I am going to change the first element of the original array.")
my_array_one[0] = 100
print(my_array_one)
print(my_array_copy)
print()


### VIEW

my_array_two = np.array([1, 2, 3, 4, 5])
print("Original array:", my_array_two)
my_array_view = my_array_two.view()
print("Array view:", my_array_view)
print(" I am going to change the first element of the array view.")
my_array_view[0] = 100
print(my_array_two)
print(my_array_view)
print("I am going to change the first element of the original array.")
my_array_two[0] = 100
print(my_array_two)
print(my_array_view)
print()


### my_array_one=my_array_two

my_array_three = np.array([1, 2, 3, 4, 5])
my_array_four = my_array_three
print("Original array:", my_array_three)
print("Original array:", my_array_four)
print(" I am going to change the first element of the original array.")
my_array_three[0] = 100
print(my_array_three)
print(my_array_four)
print("I am going to change the first element of the original array.")
my_array_two[0] = 100
print(my_array_three)
print(my_array_four)