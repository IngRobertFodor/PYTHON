from exercise_13_sum_product import calculate_sum 


print()
# Average

numbers_list_one = [1, 1.5, 5.5]
numbers_list_two = [50, 986, 1, 25, 1000]


# Average 1

def my_average(my_list):
    my_sum = 0
    my_average = 0
    #if len(my_list) == 0:
    #    return 0
    if not my_list:
        return None
    else:
        for number in my_list:
            my_sum += number
        my_average = my_sum / len(my_list)
        return print("Average of this list is:", my_average)


print("First function: Average 1")
my_average([])
my_average(numbers_list_one)
my_average(numbers_list_two)
print()


# Average 2

def my_average_with_import(my_list):
    #if len(my_list) == 0:
    #    return 0
    if not my_list:
        return None
    else:
        avg_with_import = calculate_sum(my_list) / len(my_list)
        return print("Average of this list is:", avg_with_import)


print("Second function: Average 2")
my_average_with_import([])
my_average_with_import(numbers_list_one)
my_average_with_import(numbers_list_two)