#IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest
# python -m pytest "C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest\tests\test_tdd_gilded_rose.py"


import pytest
from src.gilded_rose import Gilded_Rose


# Test case for the Gilded Rose shop
@pytest.mark.parametrize("item", [["Aged Brie", 10, 1984], ["TestItemOne", 11, 2024], ["TestItemTwo", 12, 2023]])
def test_items(item):
    gilded_rose_instance = Gilded_Rose(item)
    assert gilded_rose_instance.update_quality_value(item) == 10

def test_aged_brie_special():
    item_aged_brie = ["Aged Brie", 10, 2000]
    gilded_rose_instance = Gilded_Rose(item_aged_brie)
    assert gilded_rose_instance.update_quality_value(item_aged_brie) == 110