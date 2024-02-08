# Sum & Product

numbers_list_one = []
numbers_list_two = [50, 986, 1, 25, 1000]
numbers_list_three = [1, 1.5, 5.5]

def calculate_sum(my_list):
    sum_number = 0
    for number in my_list:
        sum_number += number 
    if len(my_list) == 0:
        return 0
    else:
        return sum_number

def calculate_product(my_list):
    multipl_number = 1
    for number in my_list:
        multipl_number *= number
    if len(my_list) == 0:
        return 1
    else:
        return multipl_number


result_one = calculate_sum(numbers_list_one)
print(result_one)
result_two = calculate_product(numbers_list_one)
print(result_two)

result_three = calculate_sum(numbers_list_two)
print(result_three)
result_four = calculate_product(numbers_list_two)
print(result_four)

result_five = calculate_sum(numbers_list_three)
print(result_five)
result_six = calculate_product(numbers_list_three)
print(result_six)