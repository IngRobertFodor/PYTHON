string = "insert 1 8"
#string = "print"
#string = "remove 10"
#string = "sort"
my_list = list(map(str, string.split()))
print(my_list)
my_list_method = my_list[0]
print(my_list_method)
my_list_other = my_list[1:]
print(my_list_other)

special_list = [10, 9]

if my_list_method == "insert":
    method = "special_list." + my_list_method + "(" + my_list_other[0] + "," + my_list_other[1] + ")"
    print(method)
    eval(method)

if my_list_method == "print":
    method = my_list_method + "(special_list)"
    print(method)

if my_list_method == "sort" or my_list_method == "pop" or my_list_method == "reverse":
    method = "special_list." + my_list_method + "()"
    print(method)
    eval(method)

if my_list_method == "remove" or my_list_method == "append":
    method = "special_list." + my_list_method + "(" + my_list_other[0] + ")"
    print(method)
    eval(method)


print(special_list)