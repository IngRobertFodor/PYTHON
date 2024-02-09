# Mode

my_list_empty = []
my_list_one = [3, 7, 10, 4, 1, 1, 6, 9, 1, 2, 8]
my_list_two = [3, 4, 7.5, 10, 4, 1, 6.99, 9, 5, 2, 8]

def mode(my_list):
    pass


# Asserts
assert mode([]) == None 
assert mode([1, 2, 3, 4, 4]) == 4 
assert mode([1, 1, 2, 3, 4]) == 1 
import random 
random.seed(42) 
testData = [1, 2, 3, 4, 4] 
for i in range(1000): 
    random.shuffle(testData) 
    assert mode(testData) == 4


result_one = mode(my_list_empty)
print(result_one)
result_two = mode(my_list_one)
print(result_two)
result_three = mode(my_list_two)
print(result_three)