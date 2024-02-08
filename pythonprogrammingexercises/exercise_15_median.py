# Median

my_list_empty = []
my_list_one = [3, 7, 10, 4, 1, 6, 9, 2, 8]
my_list_two = [3, 7, 10, 4, 1, 6, 9, 5, 2, 8]

def median(my_list):
    
    my_list.sort()
    print(my_list)
    if len(my_list) == 0:
        return None
    elif len(my_list) % 2 != 0:
        x = len(my_list) // 2
        median = my_list[x]
        return median
    else:
        x = len(my_list) // 2
        x_one = my_list[x]
        x_two = my_list[x-1]
        median = (x_one + x_two) / 2
        return median


result_one = median(my_list_empty)
print(result_one)
result_two = median(my_list_one)
print(result_two)
result_three = median(my_list_two)
print(result_three)