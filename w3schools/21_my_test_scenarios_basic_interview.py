# String Actions
a = "test"
my_list_a = []
reversed_list_a = []
for letter in a:
    my_list_a.append(letter)
print(my_list_a)
reversed_list_a = my_list_a.copy()
reversed_list_a.reverse()
print(reversed_list_a)
reversed_a = "".join(reversed_list_a)
print(reversed_a)

if my_list_a==reversed_list_a:
    print("YES")
else:
    print("NO")


# Lists Intersection
a = set(['t', 'a', 's', 't'])
b = set(['t', 's', 'e', 't'])
print(a)
print(type(a))
print(b)
print(type(b))
c = a.intersection(b)
print(c)


# Factorials
# Example if input() is 5: 1*2*3*4*5=120
# Result: 120
my_number = input("Give me the number: ")
my_number = int(my_number)
factorial = 1
for num in range(1,my_number+1):
    factorial=factorial*num
print("Factorial:",factorial)


# Basic Function 1 - Calculate Average
def calculate_average(my_list):
    my_list_sum = sum(my_list)
    average = my_list_sum/(len(my_list))
    return print("Average in my list:", average)

my_list_one = list(range(1,11))
my_list_two = list(range(11,21))

calculate_average(my_list_one)
calculate_average(my_list_two)


# Basic Function 2 - Calculate Sum of Even Numbers
def calculate_sum_even(my_list):
    sum_even= 0
    for number in my_list:
      if number%2==0:
        sum_even += number   
    return print(sum_even)

my_list_three = list(range(1,11))
my_list_four = list(range(11,21))

calculate_sum_even(my_list_three)
calculate_sum_even(my_list_four)