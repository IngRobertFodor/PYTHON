# Buy 8 Get 1 Free

def buy_eight_get_one_free(my_quantity, my_product_price):
    my_price_to_pay = 0
    for my_quantity in range(1,my_quantity+1):
        if my_quantity % 9 == 0:
            my_price_to_pay = my_price_to_pay
        else:
            my_price_to_pay += my_product_price
    return my_price_to_pay


# Asserts
assert buy_eight_get_one_free(7, 2.50) == 17.50 
assert buy_eight_get_one_free(8, 2.50) == 20 
assert buy_eight_get_one_free(9, 2.50) == 20 
assert buy_eight_get_one_free(10, 2.50) == 22.50  
for i in range(1, 4): 
    assert buy_eight_get_one_free(0, i) == 0 
    assert buy_eight_get_one_free(8, i) == 8 * i 
    assert buy_eight_get_one_free(9, i) == 8 * i 
    assert buy_eight_get_one_free(18, i) == 16 * i 
    assert buy_eight_get_one_free(19, i) == 17 * i 
    assert buy_eight_get_one_free(30, i) == 27 * i


result_one = buy_eight_get_one_free(7, 2.50)
print(result_one)
result_two = buy_eight_get_one_free(8, 2.50)
print(result_two)
result_three = buy_eight_get_one_free(9, 2.50)
print(result_three)
result_four = buy_eight_get_one_free(10, 2.50)
print(result_four)
result_five = buy_eight_get_one_free(25, 2.50)
print(result_five)