# Area & Volume

def area(length, width):
    area = length * width
    return print(str(area) + "cm2")

def perimeter(length, width):
    perimeter = length + width + length + width
    return print(str(perimeter) + "cm")

def volume(length, width, height):
    volume = length * width * height
    return print(str(volume) + "cm3")

def surface_area(length, width, height):
    surface_area = (length * width * 2) + (length * height * 2) + (width * height * 2)
    return print(str(surface_area) + "cm2")


area(10, 8)
area(1, 2)
perimeter(10, 8)
perimeter(1, 2)
volume(10, 8, 5)
volume(1, 2, 3)
surface_area(10, 8, 5)
surface_area(1, 2, 3)