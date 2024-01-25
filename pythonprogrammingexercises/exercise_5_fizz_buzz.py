# Fizz Buzz

up_to = input("Give me the number: ")
up_to = int(up_to)

def fizz_buzz(up_to):    
    range_numbers = range(1, up_to + 1)
    for number in range_numbers:
        if number % 3 == 0 and number % 5 == 0:
            number = "FizzBuzz"
        elif number % 3 == 0:
            number = "Fizz"
        elif number % 5 == 0:
            number = "Buzz"   
        else:
        # number % 3 != 0
        # number % 5 != 0
            number = number
        print(number, "", end="")


fizz_buzz(up_to)