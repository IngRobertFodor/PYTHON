import math


def calculate_hypotenuse(side_length_one, side_length_two):
    res = math.sqrt(side_length_one**2 + side_length_two**2)
    return res


result = calculate_hypotenuse(3, 4)
print(result)
# Output: 5.0