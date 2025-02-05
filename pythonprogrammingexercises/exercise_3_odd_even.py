# Odd & Even

def is_odd(number):
    text = "Number is odd: "
    if type(number) == int and number % 2 != 0:
        return print(text, True)
    elif number == 0:
        return print("Number is 0.")
    else:
        return print(text, False)
    
def is_even(number):
    text = "Number is even: "
    if type(number) == int and number % 2 == 0 and number != 0:
        return print(text, True)
    elif number == 0:
        return print("Number is 0.")
    else:
        return print(text, False)


is_odd(4)
is_odd(5)
is_odd(0)
is_odd(5.12345)
is_odd(-5)
is_odd(-5.12345)
print()

is_even(4)
is_even(5)
is_even(0)
is_even(5.12345)
is_even(-4)
is_even(-5.12345)