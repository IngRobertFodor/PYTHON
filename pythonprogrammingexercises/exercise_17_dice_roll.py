import random


# Dice roll

def dice_roll(throw_count):
    sum = 0
    for throw in range(0,throw_count):
        throw_value = random.randint(1,6)
        #print("Value of throw:",str(throw_value))
        sum += throw_value
    return sum


# Asserts
assert dice_roll(0) == 0 
assert dice_roll(1000) != dice_roll(1000) 
for i in range(1000): 
    assert 1 <= dice_roll(1) <= 6 
    assert 2 <= dice_roll(2) <= 12 
    assert 3 <= dice_roll(3) <= 18 
    assert 100 <= dice_roll(100) <= 600


result_one = dice_roll(0)
print(result_one)
result_two = dice_roll(1)
print(result_two)
result_three = dice_roll(5)
print(result_three)