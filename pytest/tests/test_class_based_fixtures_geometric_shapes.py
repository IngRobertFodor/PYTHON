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
    
    def get_perimeter(self):
        return 2 * (self.length + self.width)


class Test_geometric_shapes:

    @pytest.fixture
    def fixture_square(self):
        return Square(4, 4)
    
    @pytest.fixture
    def fixture_rectangle(self):
        return Rectangle(4, 5)

    def test_square_area(self, fixture_square):
        assert fixture_square.get_area() == 16

    def test_rectangle_area(self, fixture_rectangle):
        assert fixture_rectangle.get_area() == 20

    def test_rectangle_perimeter(self, fixture_rectangle):
        assert fixture_rectangle.get_perimeter() == 18