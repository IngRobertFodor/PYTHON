my_list = ["I", "am", "working", "."]
my_sentence = " ".join(my_list)
print(my_sentence)
print()


a = 14/3
print(a)
# Result: 4.666666666666667

a = 14/3
a = round(a)
print(round(a))
# Result: 5

a = 14/3
a = round(a,2)
print(round(a,2))
# Result: 4.67

a = 14/3
a = int(a)
print(int(a))
# Result: 4

a = 14/3
a = float(a)
print(float(a))
# Result: 4.666666666666667
print()


# This prints the sum of all of the numbers from 1 to 10
i = 0
s = 0
while i < 10:
    i = i + 1
    s = s + i
print(s)
# Result: 55
print()


    # functions
def add_numbers(i):
    if i == 0:
        return 0
    return i + add_numbers(i - 1)
print(add_numbers(4))
# Result: 10
print()


def factorial(number):
    if type(number) != int:
        print("Choose number.")
        return None
    elif number < 0:
        print("Choose number greater than zero.")
        return None
    elif number == 0:
        return 1
    i = 0
    f = 1
    while i < number:
        i = i + 1
        f = f * i
    return f
print(factorial(5))
# Result: 120
print(factorial(0))
# Result: 1
print(factorial(-5))
# Result: Choose number greater than zero., None
print(factorial("Test"))
# Result: Choose number., None
print()


def other_solution_factorial(number):
    
    if type(number) != int:
        print("Choose number.")
        return None
    elif number < 0:
        print("Choose number greater than zero.")
        return None
    elif number == 0:
        return 1    
    
    return number * other_solution_factorial(number - 1)
print(other_solution_factorial(5))
# Result: 120
print(other_solution_factorial(0))
# Result: 1
print(other_solution_factorial(-5))
# Result: Choose number greater than zero., None
print(other_solution_factorial("Test"))
# Result: Choose number., None
print()


    # *args, **kwargs
def perform_action(*args, **kwargs):
    print(args)
    print(kwargs)

perform_action(1,5, message="Sum.")
print()


    # bytes
print("Bytes.")
print(bytes(4))

smiley_bytes = bytes("😉", "utf-8")
print(smiley_bytes)
smiley_bytes.decode("utf-8")
print(smiley_bytes)
print()


    # lists
print("Lists.")
my_list = list(range(100))
print(my_list)
# result: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
print(my_list[1:51])
# result: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
print(my_list[10:51:5])
# result: [10, 15, 20, 25, 30, 35, 40, 45, 50]

aa = [0, 1, 2, 3, 4, 5]
bb = aa
aa.append(6)
print(bb)
# Result: [0, 1, 2, 3, 4, 5, 6]

aa = [0, 1, 2, 3, 4, 5]
bb = aa.copy()
aa.append(6)
print(aa)
print(bb)
# Result: [0, 1, 2, 3, 4, 5, 6] [0, 1, 2, 3, 4, 5]
print()


    # list comprehensions
print("List comprehensions.")
aa = [1, 2, 3, 4, 5]
aaaa = [2*i for i in aa]
print(aaaa)
aaaa_filtered = [i for i in aaaa if i % 10 == 0]
print(aaaa_filtered)
print()


    # dictionaries
print("Dictionaries.")
d = {"a" : 1, "b" : 2}
print(d)
e = d.get("a")
print(e)
print()


    # dictionary comprehensions
print("Dictionary comprehensions.")
dd = [("a",1),("b",2)]
# "dddd" and "eeee" are both same, but different code.
dddd = {item[0]:item[1] for item in dd}
print(dddd)
eeee = {key:value for key,value in dd}
print(eeee)
print()