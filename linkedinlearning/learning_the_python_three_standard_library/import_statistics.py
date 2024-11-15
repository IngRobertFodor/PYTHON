import statistics


data = [1, 2, 2, 3, 4, 5]

# statistics.mean()

# It is the average of a data set.
print(statistics.mean(data))
# Output: 2.8333333333333335


# statistics.median()

# It is the middle value of a data set.
# If the data set has an odd number of values, the median is the middle value.
# If the data set has an even number of values, the median is the average of the two middle values.
print(statistics.median(data))
# Output: 2.5


# statistics.mode()

# It is the value that appears most frequently in a data set.
print(statistics.mode(data))
# Output: 2


# statistics.variance()

# It is the average of the squared differences from the mean.
print(statistics.variance(data))
# Output: 2.1666666666666665


# statistics.stdev()

# It is the square root of the variance.
print(statistics.stdev(data))
# Output: 1.4719601443879744