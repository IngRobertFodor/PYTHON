    # import from Python Standard library
import time
    # import from PYTEST library
import pytest
    # import from my library
import classes
    # this is other example of import
## from classes import Motorcycle, Car


testimportone = classes.moto


print()
print(f"The time is : {time.time()}")
testimportone.turn_engine_on()

    # this pauses the execution of file for 5 sec
time.sleep(5)
print(testimportone)
    # empty row
print()