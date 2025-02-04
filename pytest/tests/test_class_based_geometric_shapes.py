import pytest


class Geometricshapes:

    def __init__(self, length, width):
        self.length = length
        self.width = width
  

class Square(Geometricshapes):

    def __init__(self, length, width):
        super().__init__(length, width)
    
    def get_area(self):
        if self.length == self.width:
            return self.length ** 2
        

class Rectangle(Geometricshapes):

    def __init__(self, length, width):
        super().__init__(length, width)

    def get_area(self):
        return self.length * self.width


class Test_geometric_shapes:

    def test_square_area(self):
        my_square = Square(4, 4)
        assert my_square.get_area() == 16

    def test_rectangle_area(self):
        my_rectangle = Rectangle(4, 5)
        assert my_rectangle.get_area() == 20