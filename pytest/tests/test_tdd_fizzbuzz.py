#IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest
# python -m pytest "C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest\tests\test_tdd_fizzbuzz.py"


import pytest
from src.fizzbuzz import fizzbuzz


# Test FizzBuzz function with a number divisible by 3 and 5.
@pytest.mark.parametrize("number", [15, 30])
def test_return_fizzbuzz(number):
    assert fizzbuzz(number) == "FizzBuzz"

# Test FizzBuzz function with a number divisible by 3.
@pytest.mark.parametrize("number", [3, 6, 9])
def test_return_fizz(number):
    assert fizzbuzz(number) == "Fizz"

# Test FizzBuzz function with a number divisible by 5.
@pytest.mark.parametrize("number", [5, 10, 20])
def test_return_buzz(number):
    assert fizzbuzz(number) == "Buzz"

# Test FizzBuzz function with different numbers not divisible by 3 or 5.
@pytest.mark.parametrize("number", [1, 2, 4, 8])
def test_return_number(number):
    assert fizzbuzz(number) == str(number)