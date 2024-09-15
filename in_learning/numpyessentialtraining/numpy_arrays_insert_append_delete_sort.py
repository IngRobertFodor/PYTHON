import numpy as np


first_array = np.array([1, 2, 3, 5])
print(first_array)


### INSERT AND APPEND

# np.insert() is used to insert a number in a specific position.

second_array = np.insert(first_array, 3, 4)
print(second_array)

# np.append() is used to append a number at the end of the array.

third_arrray = np.append(second_array, 6)
print(third_arrray)


### DELETE

# np.delete() is used to delete a number in a specific position.

fourth_array = np.delete(third_arrray, 3)
print(fourth_array)


### SORT

# np.sort() is used to sort the array.

fifth_array = np.sort([4, 2, 45, 11, 29])
print(fifth_array)
sixth_array = np.sort([4, 2, 45, 11, 29])[::-1]
print(sixth_array)
seventh_array = np.sort(sixth_array)
print(seventh_array)

two_dimensional_array = np.array([[1, 2, 5, 4], [5, 6, 9, 8]])
print("Two-dimensional array:")
print(two_dimensional_array)
print("Sort the two-dimensional array:")
print(np.sort(two_dimensional_array))

colors = np.array(["red", "blue", "green", "yellow", "purple"])
print("Colors:")
print(colors)
print("Sort the colors:")
print(np.sort(colors))