import random
# Import copy to fix asserts.
import copy


# Random Shuffle

def random_shuffle(my_list):

    len_my_list = len(my_list)
    #print("Length of my list:",len_my_list)
    random_item = random.choice(my_list)
    #print("Random item:", random_item)
    random_item_index = my_list.index(random_item)
    #print("Index of random item:",random_item_index)
    if random_item_index==0:
        random_item_index=random_item_index+1
        #print("Adjusted Index of random item:",random_item_index)
    
    for i in range(0,len_my_list):
        my_list.append(my_list[i])
    #print(my_list)

    my_list = my_list[random_item_index:random_item_index+len_my_list]
    print(my_list)

    return my_list

'''
# Asserts
random.seed(42) 
for i in range(10): 
    testData1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
    testData1_copy = copy.copy(testData1)
    random_shuffle(testData1_copy) 
    assert len(testData1_copy) == 10 
    assert testData1_copy != [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
    assert sorted(testData1_copy) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
testData2 = [] 
testData2_copy = copy.copy(testData2)
random_shuffle(testData2_copy) 
assert testData2_copy == []
'''

my_list_one = [2,4,6,8]
my_list_two = []
for i in range(1,11):
    my_list_two.append(i)
#print(my_list_two)
my_easy_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
random_shuffle(my_list_one)
random_shuffle(my_list_two)
random_shuffle(my_easy_list)