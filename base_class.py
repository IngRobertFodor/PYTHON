    # each class should have its own file
    # and then after "import" we can use (for example) methods from different files
class Vehicle:
    is_engine_on = False
    is_headlights_on = False
    make = None
    model = None

    def __init__(self, make, model):
        self.my_make = make
        self.my_model = model
    
    def __repr__(self):
        return (f'{self.my_make} {self.my_model} with engine '
                f'{"on" if self.is_engine_on else "off"} and headlights '
                f'{"on" if self.is_headlights_on else "off"}')

    def turn_engine_on(self):
        self.is_engine_on = True
        print(self.is_engine_on)
        print("Engine is turned on.")

    def turn_headlights_on(self):
        self.is_headlights_on = True
        print(self.is_headlights_on)
        print("Headlights turned on.")

    def turn_headlights_off(self):
        self.is_headlights_on = False 
        print(self.is_headlights_on)
        print("Turning headlights off.")


    # base class has general properties and methods
    # and
    # specific classes ("Motorcycle" and "Car") SHOULD have at least one property or method defined, otherways it doesn´t work


class Motorcycle(Vehicle):
    test1 = "Test1"
    print(test1)
class Car(Vehicle):
    test2 = "Test2"
    print(test2)


moto = Motorcycle("Triumph", "Thruxton")
car = Car("Mercedes", "S Class") 


for my_vehicle in [moto, car]:
    print(my_vehicle)
    my_vehicle.turn_engine_on()
    my_vehicle.turn_headlights_on()
    print()