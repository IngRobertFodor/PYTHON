from fractions import Fraction


show_expected_result = True
show_hints = False

def add_fractions(numerator1, denominator1, numerator2, denominator2):
    f_one = Fraction(numerator1, denominator1)
    f_two = Fraction(numerator2, denominator2)
    f = f_one + f_two
    res_list = (str(f).split("/"))
    updated_res_list = []
    for i in res_list:
        updated_res_list.append(int(i))
    res_tuple = tuple(updated_res_list)
    return res_tuple


numerator1 = 1
denominator1 = 2
numerator2 = 1
denominator2 = 3
result = add_fractions(numerator1, denominator1, numerator2, denominator2)
print(result)