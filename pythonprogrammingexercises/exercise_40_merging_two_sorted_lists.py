# Merging Two Sorted Lists

def two_lists_merge(list_one,list_two):
    
    merged_list = []
    while len(list_one)!=0 and len(list_two)!=0:
        if list_one[0]<list_two[0]:
            merged_list.append(list_one[0])
            list_one.remove(list_one[0])
        else:
        #list_two[0]<list_one[0]:
            merged_list.append(list_two[0])
            list_two.remove(list_two[0])

    if len(list_one)==0:
        for i in list_two:
            merged_list.append(i)
    else:
    #len(list_two)==0:
        for i in list_one:
            merged_list.append(i)

    return merged_list


# Asserts
assert two_lists_merge([1, 3, 6], [5, 7, 8, 9]) == [1, 3, 5, 6, 7, 8, 9] 
assert two_lists_merge([1, 2, 3], [4, 5]) == [1, 2, 3, 4, 5] 
assert two_lists_merge([4, 5], [1, 2, 3]) == [1, 2, 3, 4, 5] 
assert two_lists_merge([2, 2, 2], [2, 2, 2]) == [2, 2, 2, 2, 2, 2] 
assert two_lists_merge([1, 2, 3], []) == [1, 2, 3] 
assert two_lists_merge([], [1, 2, 3]) == [1, 2, 3] 


l_one = [1, 4, 5]
l_two = [5, 6, 8, 9]
print(two_lists_merge(l_one,l_two))