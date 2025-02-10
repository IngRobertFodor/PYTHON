# Smallest & Biggest

numbers_list = [50, 986, 1, 25, 1000]

def min_number(my_list):
    # If list is empty, return None.
    #if not my_list:
    #    return None
    # If list is empty, return None.
    if len(my_list) == 0:
        return None
    else:
        my_list.sort()
        print("Ascending:",my_list)
        print("Minimal number in this list is:",my_list[0])
        return my_list[0]

def max_number(my_list):
    # If list is empty, return None.
    #if not my_list:
    #    return None
    # If list is empty, return None.
    if len(my_list) == 0:
        return None
    else:
        my_list.sort(reverse=True)
        print("Descending:",my_list)
        print("Maximal number in this list is:",my_list[0])
        return my_list[0]

def min_number_using_loop(my_list):
    if len(my_list) == 0:
        return None
    else:
        my_smallest = my_list[0]
        for i in range(0, len(my_list)):
            if my_list[i] < my_smallest:
                my_smallest = my_list[i]
        print("The smallest number is:",my_smallest,".")    
        return my_smallest
            
def max_number_using_loop(my_list):
    if len(my_list) == 0:
        return None
    else:
        my_biggest = my_list[0]
        for i in range(0, len(my_list)):
            if my_list[i] > my_biggest:
                my_biggest = my_list[i]
        print("The biggest number is:",my_biggest,".")
        return my_biggest
        

result_one = min_number([])
print(result_one)
result_two = max_number([])
print(result_two)
print()

result_three = min_number(numbers_list)
print(result_three)
result_four = max_number(numbers_list)
print(result_four)
print()

result_five = min_number([28, 25, 42, 2, 28])
print(result_five)
result_six = max_number([280, 25, 42, 2, 280])
print(result_six)
print()

result_seven = min_number_using_loop([])
print(result_seven)
result_eight = max_number_using_loop([])
print(result_eight)
print()

result_nine = min_number_using_loop(numbers_list)
print(result_nine)
result_ten = max_number_using_loop(numbers_list)
print(result_ten)
print()

result_eleven = min_number_using_loop([2, 2, 2, 2, 28, 25, 42, 2, 28])
print(result_eleven)
result_twelve = max_number_using_loop([2, 2, 2, 2, 28, 25, 42, 2, 28])
print(result_twelve)