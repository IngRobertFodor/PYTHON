def alnum(s):
    my_list = list(s)
    for i in range(0, len(my_list)):
        if str((my_list[i])).isalnum():
            return True
    else:
        return False

def albe(s):
    my_list = list(s)
    for i in range(0, len(my_list)):
        if str(my_list[i]).isalpha():
            return True
    else:
        return False

def dig(s):
    my_list = list(s)
    for i in range(0, len(my_list)):
        if str((my_list[i])).isdigit():
            return True
    else:
        return False

def low(s):
    my_list = list(s)
    for i in range(0, len(my_list)):
        if str((my_list[i])).islower():
            return True
    else:
        return False

def upp(s):
    my_list = list(s)
    for i in range(0, len(my_list)):
        if str((my_list[i])).isupper():
            return True
    else:
        return False


if __name__ == '__main__':

    s = input("Enter a string: ")
    

    print(alnum(s))
    print(albe(s))
    print(dig(s))
    print(low(s))
    print(upp(s))