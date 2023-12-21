# String Actions
a = "test"
my_list = []
new_list = []
for letter in a:
  my_list.append(letter)
print(my_list)
my_list.reverse()
print(my_list)
new_list = "".join(my_list)
print(new_list)

if my_list==new_list:
  print("YES")
else:
  print("NO")


# Factorials
# Example if input() is 5: 1*2*3*4*5=120
# Result: 120
my_number = input("Give me the number: ")
my_number = int(my_number)
factorial = 1
for num in range(1,my_number+1):
  factorial=factorial*num
print("Factorial:",factorial)


# Lists Intersection
a = set(['t', 'a', 's', 't'])
b = set(['t', 's', 'e', 't'])
print(a)
print(type(a))
print(b)
print(type(b))
c = a.intersection(b)
print(c)