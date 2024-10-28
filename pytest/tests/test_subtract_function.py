import pytest


def subtract_numbers(number_one, number_two):
    return number_two - number_one


def test_subtract():
    assert subtract_numbers(4, 6) == 2