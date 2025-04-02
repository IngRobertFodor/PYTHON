# enumerate()

countries = ["United States", "United Kingdom", "France", "Germany", "Japan", "Canada", "Australia", "Brazil"]
for index, country in enumerate(countries, start=1):
    print(index, ":", country)
print()


countries = ["United States", "United Kingdom", "France", "Germany", "Japan", "Canada", "Australia", "Brazil"]
for country in enumerate(countries, start=1):
    print(country)
print()


# zip()

# Equal length lists
countries_one = ["United States", "United Kingdom", "France", "Germany", "Japan", "Canada", "Australia", "Brazil"]
capitals_one = ["Washington, D.C.", "London", "Paris", "Berlin", "Tokyo", "Ottawa", "Canberra", "Brasilia"]

country_capital_dict_one = dict(zip(countries_one, capitals_one))
print(country_capital_dict_one)
print()
for country, capital in country_capital_dict_one.items():
    print(country, capital)
print()


# Unequal length lists
# The shorter list will determine the length of the dictionary created by zip.
countries_two = ["United States", "United Kingdom", "France", "Germany", "Japan", "Canada", "Australia", "Brazil"]
capitals_two = ["Washington, D.C.", "London", "Paris", "Berlin"]

country_capital_dict_two = dict(zip(countries_two, capitals_two))
print(country_capital_dict_two)
print()
for country, capital in country_capital_dict_two.items():
    print(country, capital)
print()


# zip_longest()

# Using zip_longest() to handle unequal length lists
from itertools import zip_longest


countries_three = ["United States", "United Kingdom", "France", "Germany", "Japan", "Canada", "Australia", "Brazil"]
capitals_three = ["Washington, D.C.", "London", "Paris", "Berlin"]

country_capital_dict_three = dict(zip_longest(countries_three, capitals_three, fillvalue="Unknown"))
print(country_capital_dict_three)
print()
for country, capital in country_capital_dict_three.items():
    print(country, capital)
print()


# Unzipping a list of tuples

countries_four = ["United States", "United Kingdom", "France", "Germany", "Japan", "Canada", "Australia", "Brazil"]
capitals_four = ["Washington, D.C.", "London", "Paris", "Berlin", "Tokyo", "Ottawa", "Canberra", "Brasilia"]
country_capital_list = list(zip(countries_four, capitals_four))
country, capital = zip(*country_capital_list)
print(country)
print(capital)