#  FizzBuzz Exercise
'''
Write a program that prints the numbers until the defined number, but with the following rules:
1. For multiples of "3", print "Fizz" instead of the number.
2. For multiples of "5", print "Buzz" instead of the number.
3. For multiples of "both 3 and 5", print "FizzBuzz" instead of the number.
4. Otherwise print the number itself.
'''


def fizzbuzz(number) -> str:
    if number % 3 == 0 and number % 5 == 0:
        return "FizzBuzz"
    elif number % 3 == 0:
        return "Fizz"
    elif number % 5 == 0:
        return "Buzz"
    else:
        return str(number)