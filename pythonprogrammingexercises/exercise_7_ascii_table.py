import string


# ASCII Table

my_ordered_dictionary = {}

def print_ascii_table(num):

    x = string.printable
    id_char = []
    char = []

    for character in x: 
        if ord(character) >= 32 and ord(character) <= 126:
            print(ord(character), character)
            id_char.append(ord(character))
            char.append(character)
    
    # To create dictionary.
    my_dictionary=dict(zip(id_char, char))
    print(my_dictionary)
    
    print("ASCII position", num, "is:", my_dictionary[num])
    
    return my_dictionary[num]


result_one = print_ascii_table(35)
print(result_one)
print()
result_two = print_ascii_table(126)
print(result_two)