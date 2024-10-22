import pytest


def divide_numbers(number_one, number_two):
    return number_two / number_one


def test_divide():
    assert divide_numbers(4, 8) == 2