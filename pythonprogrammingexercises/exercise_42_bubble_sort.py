# Bubble Sort

def bubble_sort(my_list):

    list_bubble_sorted = []
    for i in range(0,len(my_list)):
        min_value = min(my_list)
        #print(min_value)
        my_list.remove(min_value)
        list_bubble_sorted.append(min_value)
        #print(list_bubble_sorted)

    return list_bubble_sorted


# Asserts
assert bubble_sort([2, 0, 4, 1, 3]) == [0, 1, 2, 3, 4] 
assert bubble_sort([2, 2, 2, 2]) == [2, 2, 2, 2]


test_list = [5,4,2,1,0]
print(bubble_sort(test_list))