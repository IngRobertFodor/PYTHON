# Fizz Buzz

up_to = input("Give me the number: ")
up_to = int(up_to)

def fizz_buzz(up_to):    
    range_numbers = range(1, up_to + 1)
    result_list = []
    for number in range_numbers:
        if number % 3 == 0 and number % 5 == 0:
            result_list.append("FizzBuzz")
        elif number % 3 == 0:
            result_list.append("Fizz")
        elif number % 5 == 0:
            result_list.append("Buzz")   
        else:
        # number % 3 != 0
        # number % 5 != 0
            result_list.append(number)
    return result_list


result_list_up_to = fizz_buzz(up_to)
print(result_list_up_to)