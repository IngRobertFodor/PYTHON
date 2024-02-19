# Leap Year

def leap_year(year):
    if year % 4 == 0:
        if year % 400 == 0:
            return True
        elif year % 100 == 0:
            return False
        else:
            return True
    else:
        return False


# Asserts
assert leap_year(1999) == False 
assert leap_year(2000) == True 
assert leap_year(2001) == False 
assert leap_year(2004) == True 
assert leap_year(2100) == False 
assert leap_year(2400) == True


#result_one = leap_year(2354)
#print(result_one)
#print()
#result_two = leap_year(2000)
#print(result_two)