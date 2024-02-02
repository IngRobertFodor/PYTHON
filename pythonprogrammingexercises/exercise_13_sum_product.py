# Sum & Product

numbers_list_one = []
numbers_list_two = [50, 986, 1, 25, 1000]
numbers_list_three = [1, 1.5, 5.5]

def calculate_sum(my_list):
    sum_number = 0
    for number in my_list:
        sum_number += number 
    if len(my_list) == 0:
        # This print is for execution of exercise 13.
        #print(0)
        # When it is commented, it is for execution of exercise 14.
        return 0
    else:
        # This print is for execution of exercise 13.
        #print(sum_number)
        # When it is commented, it is for execution of exercise 14.
        return sum_number

def calculate_product(my_list):
    multipl_number = 1
    for number in my_list:
        multipl_number *= number
    if len(my_list) == 0:
        # This print is for execution of exercise 13.
        #print(multipl_number)
        # When it is commented, it is for execution of exercise 14.
        return 1
    else:
        # This print is for execution of exercise 13.
        #print(multipl_number)
        # When it is commented, it is for execution of exercise 14.
        return multipl_number


calculate_sum(numbers_list_one)
calculate_product(numbers_list_one)

calculate_sum(numbers_list_two)
calculate_product(numbers_list_two)

calculate_sum(numbers_list_three)
calculate_product(numbers_list_three)