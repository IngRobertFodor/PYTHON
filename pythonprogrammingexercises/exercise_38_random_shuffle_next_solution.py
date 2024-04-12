import random


# Random Shuffle

def random_shuffle(my_list):
    
    random_list_values = random.sample(my_list,k=len(my_list))
    print(random_list_values)
    
    for i in range(0,len(my_list)):
        random_value = random.choice(random_list_values)
        print(random_value)
        while random_value == "Used":
            random_value = random.choice(random_list_values)
            print(random_value)   
        random_value_index = random_list_values.index(random_value)
        print(random_value_index)
        my_list[i]=random_list_values[random_value_index]
        random_list_values[random_value_index] = "Used"
        print(random_list_values)
        print("My list:",my_list)

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


random_shuffle([2,4,6,8])
#random_shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])