# Average

numbers_list_one = [1, 1.5, 5.5]
numbers_list_two = [50, 986, 1, 25, 1000]

def my_average(my_list):
    my_sum = 0
    my_average = 0
    if len(my_list) == 0:
        return print(None)
    else:
        for number in my_list:
            my_sum += number
    my_average = my_sum / len(my_list)
    
    return print("Average of this list is:", my_average)


my_average([])
my_average(numbers_list_one)
my_average(numbers_list_two)