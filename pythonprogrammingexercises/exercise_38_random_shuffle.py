import random


# Random Shuffle

def random_shuffle(my_list):
    
    original_my_list_length = len(my_list)
    for i in range(0,len(my_list)):
        my_list.append(my_list[i])
    #print(my_list)
    if original_my_list_length != 0:
        random_item = random.choice(my_list)
        #print(random_item)
        ### Using this random item index "random.choice()"", we can shuffle the list differently.
        random_item_index = my_list.index(random_item)
        #print(random_item_index)
        if random_item_index == 0:
            random_item_index = random_item_index+1
    
        my_list = my_list[random_item_index:random_item_index+original_my_list_length]
        print(my_list)

    return my_list


# Asserts
random.seed(42) 
for i in range(5): 
    testData1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
    testData1 = random_shuffle(testData1) 
    assert len(testData1) == 10 
    assert testData1 != [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
    assert sorted(testData1) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
testData2 = [] 
random_shuffle(testData2) 
assert testData2 == []


my_list_one = [2,4,6,8]
my_list_two = []
for i in range(1,11):
    my_list_two.append(i)
#print(my_list_two)
my_easy_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
random_shuffle(my_list_one)
random_shuffle(my_list_two)
random_shuffle(my_easy_list)