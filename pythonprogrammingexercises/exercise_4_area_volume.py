# Area & Volume

def area(length, width):
    area = length * width
    return area

def perimeter(length, width):
    perimeter = length + width + length + width
    return perimeter

def volume(length, width, height):
    volume = length * width * height
    return volume

def surface_area(length, width, height):
    surface_area = (length * width * 2) + (length * height * 2) + (width * height * 2)
    return surface_area


result_area_one = area(10, 8)
print(str(result_area_one) + "cm2")
result_area_two = area(1, 2)
print(str(result_area_two), "cm2")
print()

result_perimeter_one = perimeter(10, 8)
print(str(result_perimeter_one) + "cm")
result_perimeter_two = perimeter(1, 2)
print(str(result_perimeter_two), "cm")
print()

result_volume_one = volume(10, 8, 5)
print(str(result_volume_one) + "cm3")
result_volume_two = volume(1, 2, 3)
print(str(result_volume_two), "cm3")
print()

result_surface_area_one = surface_area(10, 8, 5)
print(str(result_surface_area_one) + "cm2")
result_surface_area_two = surface_area(1, 2, 3)
print(str(result_surface_area_two), "cm2")