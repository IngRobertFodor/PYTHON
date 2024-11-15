def count_valid(numbers, lower, upper):
    count = 0
    for num in numbers:
        if abs(num) in range(lower, upper+1):
            count += 1
    return count


result = count_valid([-2, 5, -20, 30, -56], 1, 30)
print(result)
# Output: 4