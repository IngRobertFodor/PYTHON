import numpy as np


## Statistics in Numpy.

a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])
c = np.array([1, 2, 3, 4, 5, 6, 7, 8]).reshape(2, 4)
# Array c:
# [[1 2 3 4]
#  [5 6 7 8]]
d = np.array([[1, 2], [3, 4], [1, 2], [4, 8]])


    ## Average of the array.

print("Average of the array:")
print(np.average(a))
# Output: 2.5
print(np.average(b))
# Output: 6.5
print(np.average(c))
# Output: 4.5
print(np.average(c, axis=0))
# Output: [3. 4. 5. 6.]
print(np.average(c, axis=1))
# Output: [2.5 6.5]
print()


    ## Mim and Max of the array.

print("Min and Max of the array:")
print(np.min(a))
# Output: 1
print(np.max(b))
# Output: 8
print()


    ## Unique values in the array.

print("Unique values in the array:")
print(np.unique(a))
# Output: [1 2 3 4]
print(np.unique(d))
# Output: [1 2 3 4 8]
print(np.unique(d, axis=0))
# Output: [[1 2]
#          [3 4]
#          [4 8]]
print(np.unique(d, axis=1))
# Output: [[1 2]
#          [3 4]
#          [1 2]
#          [4 8]]
print()


    ## Index of unique values in the array.

print("Index of unique values in the array:")
print(np.unique(a, return_index=True))
# Output: (array([1, 2, 3, 4]), array([0, 1, 2, 3]))
print(np.unique(d, return_index=True))
# Output: (array([1, 2, 3, 4, 8]), array([0, 1, 2, 3, 7]))
print()


    ## Count of unique values in the array.

print("Count of unique values in the array:")
print(np.unique(a, return_counts=True))
# Output: (array([1, 2, 3, 4]), array([1, 1, 1, 1]))
print(np.unique(d, return_counts=True))
# Output: (array([1, 2, 3, 4, 8]), array([2, 2, 1, 2, 1]))
print()