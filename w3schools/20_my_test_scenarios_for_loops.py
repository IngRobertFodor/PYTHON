    # Exercise 1
#####
#####
#####
#####
#####
hashtag = "#"
rows = 5
for row in range(1, rows+1):
    print(rows * hashtag)

# EMPTY ROW
print()


    # Exercise 2
#
##
###
####
#####
hashtag = "#"
rows = 5
for row in range(1, rows+1):
    print(row * hashtag)

# EMPTY ROW
print()


    # Exercise 3
#
##
###
####
#####
####
###
##
#
hashtag = "#"
rows = 5
for row in range(1, rows+1):
    print(row * hashtag)
for row in range(rows-1,0,-1):
    print(row * hashtag)

# EMPTY ROW
print()


    # Exercise 4
# Print the sum of all numbers from 1 to 100.
sum = 0
for num in range(1,101):
    sum+=num
    print(sum)
print("This is the result:", sum)

# EMPTY ROW
print()


    # Exercise 5
# Print even numbers from range from 1 to 20.
result_numbers = []
for num in range(1,21):
    if num%2 == 0:
        result_numbers.append(num)
print(result_numbers)

# EMPTY ROW
print()


    # Exercise 6
# Print factorial of given number.
number = 4
factorial = 1
for i in range(1,number+1):
    factorial = factorial*i
    print(factorial)

# EMPTY ROW
print()


    # Exercise 7
# Write a program that prints a multiplication table.
# The program should ask the user for the maximum number and then print a multiplication table from 1 to that number.
# For example, if the user enters 5, the program should print the following table:
'''
1  2  3  4  5
2  4  6  8  10
3  6  9  12 15
4  8  12 16 20
5  10 15 20 25
'''
number=input("Give me number: ")
number=int(number)
print("Number is:", number)
for number_in_first_row in range(1,number+1):
    for row in range(1,number+1):
        print(number_in_first_row*row, "", end="")
    print()

# EMPTY ROW
print()


    # Exercise  8.1
# Write a program that prints a diamond shape made of numbers.
'''
1
22
333
4444
55555
'''
number=input("Give me number: ")
number=int(number)
print("Number is:", number)
for row_number in range(1,number+1):
    print(row_number*str(row_number), "", end="")
    print()

# EMPTY ROW
print()


    # Exercise  8.2
# Cleaner Code.
# Write a program that prints a diamond shape made of numbers.
'''
    1
   2 2
  3 3 3
 4 4 4 4
5 5 5 5 5
'''
number=input("Give me number: ")
number=int(number)
print("Number is:", number)
for row_number in range(1, number + 1):
        # Print spaces
        for a in range(number - row_number):
            print(" ", end="")
        # Print numbers
        for b in range(row_number):
            print(row_number, "", end="")
        # Move to the next line
        print()