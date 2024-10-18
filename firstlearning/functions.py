num111 = 8
num1111 = 2
def do_math(num111, num1111):
    result = num111 + num1111
    result = result - 1
    result = result * 2.5
    result = result - num111
    return result

print(do_math(num111, num1111))
print(do_math(num111, 8))


num11 = 4
def new_math(num11, num22=2, num33=3):
    result = num11 + num22
    return result

print(new_math(num11, num22=5))