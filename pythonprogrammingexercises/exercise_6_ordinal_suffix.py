import random


# Ordinal Suffix

def ordinal_suffix(number):

    number=str(number)
    last_num = number[-1:]
    last_two_nums = number[-2:]
    
    if int(last_two_nums) in range(11,14):
        suffix = "th"
        result = number + suffix
        return print(result)
    elif int(last_num) == 0:
        suffix = "th"
        result = number + suffix
        return print(result)
    elif int(last_num) == 1:
        suffix = "st"
        result = number + suffix
        return print(result)
    elif int(last_num) == 2:
        suffix = "nd"
        result = number + suffix
        return print(result)
    elif int(last_num) == 3:
        suffix = "rd"
        result = number + suffix
        return print(result)
    elif int(last_num) in range (4,10):
        suffix = "th"
        result = number + suffix
        return print(result)
        

ordinal_suffix(0)
ordinal_suffix(1)
ordinal_suffix(2)
ordinal_suffix(3)
ordinal_suffix(4)
ordinal_suffix(5)
ordinal_suffix(6)
ordinal_suffix(7)
ordinal_suffix(8)
ordinal_suffix(9)
ordinal_suffix(10)
ordinal_suffix(11)
ordinal_suffix(12)
ordinal_suffix(13)
ordinal_suffix(14)
ordinal_suffix(15)
ordinal_suffix(21)
ordinal_suffix(22)
ordinal_suffix(23)
ordinal_suffix(24)
ordinal_suffix(25)
ordinal_suffix(30)
ordinal_suffix(101)
ordinal_suffix(80)