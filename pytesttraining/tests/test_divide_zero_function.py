import pytest


def divide_numbers(number_one, number_two):
    return number_two / number_one


def test_divide():
    with pytest.raises(ZeroDivisionError):
        assert divide_numbers(0, 4)