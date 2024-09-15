import numpy as np


## Aritmetic operations with arrays.

print("Aritmetic operations with arrays.")
print()
a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])
print("Array a:", a)
print("Array b:", b)
print()


    ## Sum function.

print("Sum function.")
print(np.sum(a))
# Sum Output: 10
print(np.sum(np.arange(1, 10).reshape(3, 3)))
# Sum Output: 45
print(np.sum(np.arange(1, 10).reshape(3, 3), axis=0))
# Array Output: [[1 2 3]
#          [4 5 6]
#          [7 8 9]]
# Sum Output: [12 15 18]
print(np.sum(np.arange(1, 10).reshape(3, 3), axis=1))
# Array Output: [[1 2 3]
#          [4 5 6]
#          [7 8 9]]
# Sum Output: [ 6 15 24]
print()


    # Adding two arrays.

print("Adding two arrays.")
print(a + b)
print(np.add(a, b))
print()


    # Subtracting two arrays.

print("Subtracting two arrays.")
print(b - a)
print(np.subtract(b, a))
print()


    # Multiplying two arrays.

print("Multiplying two arrays.")
print(a * b)
print(np.multiply(a, b))
# Array *
print(a * 8)
print()


    # Dividing two arrays.

print("Dividing two arrays.")
print(b / a)
print(b // a)
print(b / 2)
print(np.divide(b, a))
print()


    # Square root (oposite of power) of the array.

print("Square root (oposite of power) of the array.")
print(np.sqrt(a))
# Output: [1.         1.41421356 1.73205081 2.        ]
print()


    # Power of the array.

print("Power of the array.")
print(np.power(a, 2))
# Output: [1 4 9 16]
print(np.power(a, 4))
# Output: [1 16 81 256]
c = 2
print(np.power(a, c))
# Output: [1 4 9 16]
print(a**c)
# Output: [1 4 9 16]
print(a**2)
# Output: [1 4 9 16]
print()


    # Modulus (%) of the array.

print("Modulus (%) of the array.")
print(np.mod(a, 2))
# Output: [1 0 1 0]
print()


    # Exponential of the array.

print("Exponential of the array.")
print(np.exp(a))
# Output: [ 2.71828183  7.3890561  20.08553692 54.59815003]
print()


    # Broadcasting. Special adding two arrays.

print("Broadcasting. Special adding two arrays.")
d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
e = np.array([2, 2, 2])
f = np.array([3, 3])
g = np.arange(24).reshape(2, 3, 4)
# Array g:
# [[[ 0  1  2  3]
#   [ 4  5  6  7]
#   [ 8  9 10 11]]
#  [[12 13 14 15]
#   [16 17 18 19]
#   [20 21 22 23]]]
h = np.array([0, 1, 2, 3])
# Array h:
# [0 1 2 3]
print()

print(d+e)
    # Compatible arrays.
# Output: [[ 3  4  5]
#          [ 6  7  8]
#          [ 9 10 11]]
print()

print(g-h)
    # Compatible arrays.
# Output: [[[ 0  0  0  0]
#           [ 4  4  4  4]
#           [ 8  8  8  8]]
#          [[12 12 12 12]
#           [16 16 16 16]
#           [20 20 20 20]]]
print()

print(d+f)
    # Incompatible arrays.
# Output: ValueError: operands could not be broadcast together with shapes (3,3) (2,)
print()