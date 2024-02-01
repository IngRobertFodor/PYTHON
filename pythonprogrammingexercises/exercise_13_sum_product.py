# Sum & Product

numbers_list_one = []
numbers_list_two = [50, 986, 1, 25, 1000]
numbers_list_three = [1, 1.5, 5.5]

def calculate_sum(my_list):
    sum_number = 0
    for number in my_list:
        sum_number += number 
    if len(my_list) == 0:
        return print(0)
    else:
        return print(str(sum_number))

def calculate_product(my_list):
    multipl_number = 1
    for number in my_list:
        multipl_number *= number
    if len(my_list) == 0:
        return print(1)
    else:
        return print(multipl_number)


calculate_sum(numbers_list_one)
calculate_product(numbers_list_one)

calculate_sum(numbers_list_two)
calculate_product(numbers_list_two)

calculate_sum(numbers_list_three)
calculate_product(numbers_list_three)