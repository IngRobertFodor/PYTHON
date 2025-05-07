#IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest
# python -m pytest "C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest\tests\test_tdd_money.py"


import pytest
from src.money import Money


# Test Money class with currency conversion from USD to USD
def test_money_conversion_USD_to_USD():
    USD = Money(100, 'USD', 1.0, 'USD')
    assert USD.convert() == 100.0
    
# Test Money class with currency conversion from USD to EUR
def test_money_conversion_USD_to_EUR():
    EUR = Money(100, 'USD', 0.85, 'EUR')
    assert EUR.convert() == 85.0

# Test e_wallet addition with both conversions
def test_add_to_e_wallet():
    e_wallet = 0.0
    USD = Money(100, 'USD', 1.0, 'USD')
    e_wallet += USD.convert()
    assert e_wallet == 100.0
    EUR = Money(100, 'USD', 0.85, 'EUR')
    e_wallet = USD.convert() + EUR.convert()
    assert e_wallet == 185.0

# Test remove 5.0 from e_wallet ("-" conversion rate)
def test_remove_from_e_wallet():
    e_wallet = 185.0
    EUR = Money(100, 'USD', -0.05, 'EUR')
    e_wallet += EUR.convert()
    assert e_wallet == 180.0