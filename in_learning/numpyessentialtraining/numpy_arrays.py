import numpy as np


### ARRAY

# np.array() is used to create an array.

# Arrays are similar to lists in Python, but they are more efficient.
# Are used to store data of the same data type (int, float, str, etc).
# Advantages of arrays are:
    # are memory efficient,
    # are faster than lists,
    # are optimized for mathematical operations.

## dtype

# dtype is the data type of the array.
print("Array")
integers = np.array([1, 2, 3, 4, 5])
print(integers)
print("Array's d-type:", integers.dtype)
print("Array")
small_integers = np.array([1, 2, 3, 4, 5], dtype=np.int8)
print(small_integers)
print("Array's d-type:", small_integers.dtype)
print()


## Two-dimensional array

print("Two-dimensional array")
# This is an example of 2-dimensional array.
two_dimensional_array = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
print(two_dimensional_array)
# Access number 6 of the two-dimensional array.
print("This will print the number of dimensions in my array:", two_dimensional_array.ndim)
print("Access number 6 of the two-dimensional array:", two_dimensional_array[1, 1])
print()


## N_dimensional array

print("N-dimensional array")
# This is an example of 3-dimensional array.
n_dimensional_array = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
print(n_dimensional_array)
# Access number 6 of the n-dimensional array.
print("This will print the number of dimensions in my array:", n_dimensional_array.ndim)
print("Access number 6 of the n-dimensional array:", n_dimensional_array[1, 0, 1])
print()


## Array from list.

print("Array from list.")
int_list = [1, 2, 3, 4, 5]
array_from_int_list = np.array(int_list)
print(array_from_int_list)

str_list = ["1", "2", "3", "4", "5"]
array_from_str_list = np.array(str_list)
print(array_from_str_list)

# In case of combining different data types, the array will convert all data types in the list to a single data type.
combined_list = [1, 2, "3", 4, 5]
array_from_combined_list = np.array(combined_list)
print(array_from_combined_list)

# Array from multidimensional list.
print("Array from multidimensional list.")
multidimensional_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
array_from_multidimensional_list = np.array(multidimensional_list)
print(array_from_multidimensional_list)
print()


## Array from tuple.

print("Array from tuple.")
int_tuple = (1, 2, 3, 4, 5)
array_from_int_tuple = np.array(int_tuple)
print(array_from_int_tuple)
print()


## List from array.

print("List from array.")
list_from_array = array_from_int_list.tolist()
print(list_from_array)