import string
import collections


# Rot 13 Encryption

def encryption(my_text):

    id_char_lowercase = []
    char_lowercase = []
    id_char_uppercase = []
    char_uppercase = []
    encrypted_my_text = []

    for lowercase_character in string.ascii_lowercase: 
        if ord(lowercase_character) >= 97 and ord(lowercase_character) <= 122:
            #print(ord(lowercase_character), " ", lowercase_character)
            id_char_lowercase.append(ord(lowercase_character))
            char_lowercase.append(lowercase_character)
    
    for uppercase_character in string.ascii_uppercase: 
        if ord(uppercase_character) >= 65 and ord(uppercase_character) <= 90:
            #print(ord(uppercase_character), " ", uppercase_character)
            id_char_uppercase.append(ord(uppercase_character))
            char_uppercase.append(uppercase_character)
    
    # To create dictionary.
    my_dictionary_lowercase=dict(zip(id_char_lowercase,char_lowercase))
    # To order dictionary.
    my_dictionary_lowercase = collections.OrderedDict(sorted(my_dictionary_lowercase.items()))
    #print(my_dictionary_lowercase)
    
    # To create dictionary.
    my_dictionary_uppercase=dict(zip(id_char_uppercase,char_uppercase))
    # To order dictionary.
    my_dictionary_uppercase = collections.OrderedDict(sorted(my_dictionary_uppercase.items()))
    #print(my_dictionary_uppercase)

    for letter in my_text:
        if letter in string.ascii_lowercase or letter in string.ascii_uppercase:
            if letter in string.ascii_lowercase:
                ord_letter = ord(letter)+13                
                if ord_letter > 122:
                    ord_letter = 96+(ord_letter-122)
                    #print(ord_letter)
                else:
                    ord_letter = ord_letter
                    #print(ord_letter)
                yy = my_dictionary_lowercase.get(ord_letter)       
                #print(yy)
                encrypted_my_text.append(yy)
            elif letter in string.ascii_uppercase:
                ord_letter = ord(letter)+13
                if ord_letter > 90:
                    ord_letter = 64+(ord_letter-90)
                    #print(ord_letter)
                else:
                    ord_letter = ord_letter
                    #print(ord_letter)
                zz = my_dictionary_uppercase.get(ord_letter)
                #print(zz)
                encrypted_my_text.append(zz)
        else:
            encrypted_my_text.append(letter)

    string_encrypted_my_text = "".join(encrypted_my_text)

    return string_encrypted_my_text


# Asserts
assert encryption('Hello, world!') == 'Uryyb, jbeyq!' 
assert encryption('Uryyb, jbeyq!') == 'Hello, world!' 
assert encryption(encryption('Hello, world!')) == 'Hello, world!' 
assert encryption('abcdefghijklmnopqrstuvwxyz') == 'nopqrstuvwxyzabcdefghijklm' 
assert encryption('ABCDEFGHIJKLMNOPQRSTUVWXYZ') == 'NOPQRSTUVWXYZABCDEFGHIJKLM'


my_test_text = "Hello, world!"
print(encryption(my_test_text))