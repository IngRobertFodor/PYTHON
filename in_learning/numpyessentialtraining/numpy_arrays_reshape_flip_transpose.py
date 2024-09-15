import numpy as np


### RESHAPE

print("RESHAPE")

# Create a 1D array
a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
print(a)

# Reshape the 1D array to a 2D array
b = np.reshape(a, (4, 3))
print("2D array: ", b)

# Reshape the 1D array to a 3D array
c = np.reshape(a, (3, 2, 2))
print("3D array: ", c)

# Reshape the 2D array to a 1D array with -1
d = np.reshape(b, -1)
print("1D array: ", d)
print()


### REVERSE AND FLIP

print("REVERSE AND FLIP")

# We can use slicing "-1". It will reverse the array.
print("Reversed 1D array: ", a[::-1])
# Output: [12 11 10  9  8  7  6  5  4  3  2  1]
print()

# Flip()
print("Flipped 1D array: ", np.flip(a))
# Output: [12 11 10  9  8  7  6  5  4  3  2  1]
print()

print("Flipped 2D array: ", np.flip(b))
# Output: [[12 11 10]
#          [ 9  8  7]
#          [ 6  5  4]
#          [ 3  2  1]]
print()

print("Flipped 2D array: ", np.flip(b, axis=0))
# Output: [[ 10 11 12]
#          [  7  8  9]
#          [  4  5  6]
#          [  1  2  3]]
print()

print("Flipped 2D array: ", np.flip(b, axis=1))
# Output: [[ 3  2  1]
#          [ 6  5  4]
#          [ 9  8  7]
#          [12 11 10]]
print()


### TRANSPOSE

# Transpose array means to change the rows into columns and columns into rows.

print("TRANSPOSE")

test_array = np.arange(12).reshape(3, 4)
print("Original array: ", test_array)
# Output: [[ 0  1  2  3]
#          [ 4  5  6  7]
#          [ 8  9 10 11]]

transposed_array = np.transpose(test_array)
print("Transposed array: ", transposed_array)
# Output: [[ 0  4  8]
#          [ 1  5  9]
#          [ 2  6 10]
#          [ 3  7 11]]
print()