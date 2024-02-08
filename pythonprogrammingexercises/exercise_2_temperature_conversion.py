# Temperature Conversion

def convert_to_fahrenheit(degrees_celsius):
    degrees_fahrenheit = degrees_celsius * (9 / 5) + 32
    return degrees_fahrenheit

def convert_to_celsius(degrees_fahrenheit):
    degrees_celsius = (degrees_fahrenheit - 32) * (5 / 9)
    return degrees_celsius


result_one = convert_to_celsius(0)
print(result_one)
result_two = convert_to_celsius(180)
print(result_two)

result_three = convert_to_fahrenheit(0)
print(result_three)
result_four = convert_to_fahrenheit(100)
print(result_four)