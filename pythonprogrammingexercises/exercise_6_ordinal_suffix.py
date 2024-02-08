# Ordinal Suffix

def ordinal_suffix(number):

    number=str(number)
    last_num = number[-1:]
    last_two_nums = number[-2:]
    
    if int(last_two_nums) in range(11,14):
        suffix = "th"
        result = number + suffix
        return result
    elif int(last_num) == 0:
        suffix = "th"
        result = number + suffix
        return result
    elif int(last_num) == 1:
        suffix = "st"
        result = number + suffix
        return result
    elif int(last_num) == 2:
        suffix = "nd"
        result = number + suffix
        return result
    elif int(last_num) == 3:
        suffix = "rd"
        result = number + suffix
        return result
    elif int(last_num) in range (4,10):
        suffix = "th"
        result = number + suffix
        return result
        

result_ordinal_suffix_zero = ordinal_suffix(0)
print(result_ordinal_suffix_zero)
result_ordinal_suffix_one = ordinal_suffix(1)
print(result_ordinal_suffix_one)
result_ordinal_suffix_two = ordinal_suffix(2)
print(result_ordinal_suffix_two)
result_ordinal_suffix_three = ordinal_suffix(3)
print(result_ordinal_suffix_three)
result_ordinal_suffix_four = ordinal_suffix(4)
print(result_ordinal_suffix_four)
result_ordinal_suffix_five = ordinal_suffix(5)
print(result_ordinal_suffix_five)
result_ordinal_suffix_six = ordinal_suffix(6)
print(result_ordinal_suffix_six)
result_ordinal_suffix_seven = ordinal_suffix(7)
print(result_ordinal_suffix_seven)
result_ordinal_suffix_eight = ordinal_suffix(8)
print(result_ordinal_suffix_eight)
result_ordinal_suffix_nine = ordinal_suffix(9)
print(result_ordinal_suffix_nine)
result_ordinal_suffix_ten = ordinal_suffix(10)
print(result_ordinal_suffix_ten)
result_ordinal_suffix_eleven = ordinal_suffix(11)
print(result_ordinal_suffix_eleven)
result_ordinal_suffix_twelve = ordinal_suffix(12)
print(result_ordinal_suffix_twelve)
result_ordinal_suffix_thirteen = ordinal_suffix(13)
print(result_ordinal_suffix_thirteen)
result_ordinal_suffix_fourteen = ordinal_suffix(14)
print(result_ordinal_suffix_fourteen)
result_ordinal_suffix_fifteen = ordinal_suffix(15)
print(result_ordinal_suffix_fifteen)
result_ordinal_suffix_twentyone = ordinal_suffix(21)
print(result_ordinal_suffix_twentyone)
result_ordinal_suffix_twentytwo = ordinal_suffix(22)
print(result_ordinal_suffix_twentytwo)
result_ordinal_suffix_twentythree = ordinal_suffix(23)
print(result_ordinal_suffix_twentythree)
result_ordinal_suffix_twentyfour = ordinal_suffix(24)
print(result_ordinal_suffix_twentyfour)
result_ordinal_suffix_twentyfive = ordinal_suffix(25)
print(result_ordinal_suffix_twentyfive)
result_ordinal_suffix_thirty = ordinal_suffix(30)
print(result_ordinal_suffix_thirty)
result_ordinal_suffix_hundredone = ordinal_suffix(101)
print(result_ordinal_suffix_hundredone)
result_ordinal_suffix_eighty = ordinal_suffix(80)
print(result_ordinal_suffix_eighty)