import numpy as np


### SLICING AND ACCESSING ELEMENTS

# Access number 6 of the two-dimensional array.
two_dimensional_array = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
print(two_dimensional_array)
print("This will print the number of dimensions in my array:", two_dimensional_array.ndim)
print("Access number 6 of the two-dimensional array:", two_dimensional_array[1, 1])
print()
# Access number 6 of the n-dimensional array.
n_dimensional_array = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
print(n_dimensional_array)
print("This will print the number of dimensions in my array:", n_dimensional_array.ndim)
print("Access number 6 of the n-dimensional array:", n_dimensional_array[1, 0, 1])
print()


# Accessing elements using negative indexes.
print("Access number 8 of the n-dimensional array using negative indexes:", n_dimensional_array[1, -1, -1])
print()


# Accessing a range of elements.
my_array = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print("Access the first 5 elements of my_array:", my_array[:5])
print("Access every second of the first 5 elements of my_array:", my_array[:5:2])
print()


# Accessing whole row or column.
print("Access the first row of the two-dimensional array:", two_dimensional_array[0,: ])
print("Access the first column of the two-dimensional array:", two_dimensional_array[ :,0])
print()
print("Access the first row of the n-dimensional array:", n_dimensional_array[0,: ])
print("Access the first column of the n-dimensional array:", n_dimensional_array[ :,0])
print()
print("Access the second row of the n-dimensional array:", n_dimensional_array[1,: ])
print()