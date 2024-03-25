from itertools import batched


# Comma-Formated Numbers

def comma_format(number):
    
    # The adjusted number. Whole number and decimals.
    number = str(number)
    print(number)
    split_number = number.split(".")
    print(split_number)
    whole_number = split_number[0]
    print(whole_number)

    # List of the number.
    list_number = []
    for i in whole_number:
        list_number.append(i)
    print(list_number)
    
    # Reverse the list.
    list_number.reverse()
    print(list_number)
    
    # Add "," after every third number.
    special_number = []
    count = 0
    for i in list_number:
        special_number.append(i)
        count+=1
        if count % 3 == 0:
            special_number.append(",")
    print(special_number)
    
    # Remove "," at the beginning of the number.
    special_number.reverse()
    if special_number[0] == ",":
        special_number.pop(0)
    print(special_number)
    
    # The adjusted number. Whole number and decimals.
    first_part_whole_number = "".join(special_number)
    num = str()
    if "." in number:
        second_part_decimals = split_number[1]
        num = first_part_whole_number + "." + second_part_decimals
    else:
        num = first_part_whole_number

    return num


# Asserts
assert comma_format(1) == '1' 
assert comma_format(10) == '10' 
assert comma_format(100) == '100' 
assert comma_format(1000) == '1,000' 
assert comma_format(10000) == '10,000' 
assert comma_format(100000) == '100,000' 
assert comma_format(1000000) == '1,000,000' 
assert comma_format(1234567890) == '1,234,567,890' 
assert comma_format(1000.123456) == '1,000.123456' 


print()
print("Result is:",comma_format(55448))
print("Result is:",comma_format(-55448))
print("Result is:",comma_format(8))
print("Result is:",comma_format(5544812345))
print("Result is:",comma_format(-55448.1234))
print("Result is:",comma_format(55448.1234))