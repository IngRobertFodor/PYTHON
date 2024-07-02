import string


def alphabet_rangoli(n):
    
    alphabet = string.ascii_lowercase
    my_list = list(alphabet)
    print(my_list)
    print()
    # this is the same as the previous solution (26 letters of the alphabet)
    # alphabet = 'abcdefghijklmnopqrstuvwxyz'

    # compute the width of the string to be printed as centered
    width = ((2*n)-1) + ((2*n) - 2)

    for i in range(0,n-1):
        i_one = my_list[n-1:n-1-i:-1]
        i_two = my_list[n-1-i:n]
        line = "-".join(i_one + i_two)
        # this will print the line centered
        print(line.center(width, "-"))
    for i in range(0,n):
        i_three = my_list[n-1:i:-1]
        i_four = my_list[i:n]
        line = "-".join(i_three + i_four)
        # this will print the line centered 
        print(line.center(width, "-"))


alphabet_rangoli(5)