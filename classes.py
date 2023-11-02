class Motorcycle:
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


moto = Motorcycle("Triumph", "Thruxton")
    # this will display the whole information about object
print(moto)

moto.turn_engine_on()
moto.turn_headlights_on()
print(moto)

moto.turn_headlights_off()
print(moto)


    #############################################


class Car:
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


car = Car("Mercedes", "S Class")
print(car)

car.turn_engine_on()
print(car)