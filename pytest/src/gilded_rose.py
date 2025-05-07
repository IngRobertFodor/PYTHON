# Gilded Rose Exercise


import datetime


class Gilded_Rose:
    
    def __init__(self, item):
        self.item = item
    
    def update_quality_value(self, item):
        # Update the quality value of the item based on:
        # 1. its name and
        # 2. the number of days passed.
        current_year = int(datetime.datetime.now().year)
        year = item[2]
        year_diffrence = current_year - year
        if item[0] != "Aged Brie":
            item[1] -= 1*year_diffrence
            return item[1]
        elif item[0] == "Aged Brie" and year == 2000:
            item[1] += 100
            return item[1]
        else:
            return item[1]