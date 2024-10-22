import pytest


def add_numbers(number_one, number_two):
    return number_one + number_two


def test_add():
    assert add_numbers(2, 4) == 6