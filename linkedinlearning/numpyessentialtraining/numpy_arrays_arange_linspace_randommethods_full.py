import numpy as np


### ARANGE

# np.arange() is used to create an array with a range of elements.
# np.arange(start, stop, step)

array_arange_one = np.arange(10)
print("Array arange:", array_arange_one)
print()
array_arange_two = np.arange(0, 10)
print("Array arange:", array_arange_two)
print()
array_arange_three = np.arange(1, 10, 2)
print("Array arange:", array_arange_three)
print()


### LINSPACE

# np.linspace() is used to create an array with a range of elements.
# ARANGE VS LINSPACE - The difference between arange and linspace is that linspace returns an array with a specific number of elements (number_of_elements).
# np.linspace(start, stop, number_of_elements)

array_linspace_one = np.linspace(2, 10, 4) 
print("Array linspace:", array_linspace_one)
print()


### RANDOM

# np.random.rand() is used to create an array with random numbers (between 0 and 1).
# One dimension array: np.random.rand(number_of_elements)
# Two dimensions array: np.random.rand(rows, columns)
# Three dimensions array: np.random.rand(layers, rows, columns)

array_random_one = np.random.rand(5)
print("Array rand:", array_random_one)
print()
array_random_two = np.random.rand(2, 3)
print("Array rand:", array_random_two)
print()
array_random_three = np.random.rand(2, 3, 4)
print("Array rand:", array_random_three)
print()

# np.random.randint() is used to create an array with random integers (elements can repeat).
# np.random.randint(start, stop, number_of_elements)
# One dimension array: np.random.randint(start, stop, number_of_elements)
# Two dimensions array: np.random.randint(start, stop, (rows, columns))
# Three dimensions array: np.random.randint(start, stop, (layers, rows, columns))

array_random_four = np.random.randint(1, 10, 5)
print("Array randint:", array_random_four)
print()


### FULL

# np.full() is used to create an array with a specific number.
# np.full((rows, columns), number)

array_full_one = np.full((2, 3), 8) 
print("Array full:", array_full_one)
# Result is: [[8 8 8]
#             [8 8 8]]
print()


### SHAPE, SIZE

# np.shape() is used to get the shape of an array.
# np.size() is used to get the size of an array.