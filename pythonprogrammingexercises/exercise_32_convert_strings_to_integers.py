# Convert Strings To Integers

def convert_str_to_int(my_string_num):
    my_dict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9}
    #print(my_dict.keys())
    
    my_number_list = list(my_string_num)
    #print(my_number_list)
    
    my_number_list_new = []
    for i in my_number_list:    
        if i in my_dict.keys():
            ii = my_dict.get(i)
            my_number_list_new.append(ii)
    #print(my_number_list_new)
    
    result = 0
    for num in my_number_list_new:
        result = num + result*10    
    if my_number_list[0] == "-":
        result = -1 * result
    return result


# Asserts
for i in range(-10000, 10000): 
    assert convert_str_to_int(str(i)) == i


result_one = convert_str_to_int("20")
print(result_one)
result_two = convert_str_to_int("-50")
print(result_two)