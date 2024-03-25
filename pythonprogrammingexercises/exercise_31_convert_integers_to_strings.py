# Convert Integers To Strings

def convert_int_to_str(my_number):
    my_string_num = "{}".format(my_number)
    #print(type(my_string_num))
    return my_string_num


# Asserts
for i in range(-10000, 10000): 
    assert convert_int_to_str(i) == str(i)


result_one = convert_int_to_str(20)
print(result_one)
result_two = convert_int_to_str(-50)
print(result_two)