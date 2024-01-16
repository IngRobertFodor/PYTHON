import random


# Ordinal Suffix

def ordinal_suffix(number):

    number=str(number)
    print(number)
    number_list = list(number)
    last_num = number_list[-1]
    print("This letter decide about the suffix: " + str(last_num))

    if int(last_num) == 0:
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
        

ordinal_suffix(80)
ordinal_suffix(21)
ordinal_suffix(22)
ordinal_suffix(23)
ordinal_suffix(24)
ordinal_suffix(25)
ordinal_suffix(26)
ordinal_suffix(27)
ordinal_suffix(28)
ordinal_suffix(29)
ordinal_suffix(50)