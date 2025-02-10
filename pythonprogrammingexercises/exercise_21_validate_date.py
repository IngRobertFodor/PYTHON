import datetime
from exercise_20_leap_year import leap_year


print()
# Validate Date

def validate_date(year,month,day):
    
    #print()
    leap_year_check = leap_year(year)
    #print("Is this the leap year?:",leap_year_check)
    #print()
    
    if day in range(1,28) and month in range(1,13):
        return True
    elif day in range(28,32) and month in range(1,13):
        if month == 2 and day == 28:
            return True
        elif month == 2 and day == 29 and leap_year_check == True:
            return True
        elif day in [28, 29, 30, 31] and month in [1, 3, 5, 7, 8, 10, 12]:
            return True
        elif day in [28, 29, 30] and month in [4, 6, 9, 11]:
            return True
        else:
            return False
    else:
        return False


# Asserts
assert validate_date(1999, 12, 31) == True 
assert validate_date(2000, 2, 29) == True 
assert validate_date(2001, 2, 29) == False 
assert validate_date(2029, 13, 1) == False 
assert validate_date(1000000, 1, 1) == True 
assert validate_date(2015, 4, 31) == False 
assert validate_date(1970, 5, 99) == False 
assert validate_date(1981, 0, 3) == False 
assert validate_date(1666, 4, 0) == False  
d = datetime.date(1970, 1, 1) 
oneDay = datetime.timedelta(days=1) 
for i in range(1000000): 
    assert validate_date(d.year, d.month, d.day) == True 
    d += oneDay


print(validate_date(2400, 2, 29))
print(validate_date(2100, 2, 29))
print(validate_date(2000, 2, 29))
print(validate_date(2024, 8, 15))