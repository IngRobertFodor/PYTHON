# Bubble Sort

def bubble_sort(my_list):

    for i in range(0,len(my_list)-1):
        for j in range(i,len(my_list)):
            if my_list[j]<my_list[i]:
                my_list[i], my_list[j] = my_list[j], my_list[i]

    return my_list


# Asserts
assert bubble_sort([2, 0, 4, 1, 3]) == [0, 1, 2, 3, 4] 
assert bubble_sort([2, 2, 2, 2]) == [2, 2, 2, 2]


test_list = [5,4,2,1,0]
print(bubble_sort(test_list))