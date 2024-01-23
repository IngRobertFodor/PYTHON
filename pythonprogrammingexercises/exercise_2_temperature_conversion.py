# Temperature Conversion

def convert_to_fahrenheit(degrees_celsius):
    degrees_fahrenheit = degrees_celsius * (9 / 5) + 32
    return print(degrees_fahrenheit)

def convert_to_celsius(degrees_fahrenheit):
    degrees_celsius = (degrees_fahrenheit - 32) * (5 / 9)
    return print(degrees_celsius)


convert_to_celsius(0)
convert_to_celsius(180)

convert_to_fahrenheit(0)
convert_to_fahrenheit(100)