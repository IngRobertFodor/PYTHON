import string


# Uppercase Letters

def get_uppercase(my_text):
    
    lowercase = str(string.ascii_lowercase)
    #print("Lowercase string:",lowercase)
    #print(type(lowercase))

    uppercase = str(string.ascii_uppercase)
    #print("Uppercase string:",uppercase)
    #print(type(uppercase))
    
    for character in my_text:
        if character in lowercase:
            character_index_l = lowercase.index(character)
            #print(character_index_l)
            #print(lowercase[character_index_l])
            my_text = my_text.replace(lowercase[character_index_l], uppercase[character_index_l])
            #print(my_text)
        else:
            continue

    return my_text


# Asserts
assert get_uppercase('Hello') == 'HELLO' 
assert get_uppercase('hello') == 'HELLO' 
assert get_uppercase('HELLO') == 'HELLO' 
assert get_uppercase('Hello, world!') == 'HELLO, WORLD!' 
assert get_uppercase('goodbye 123!') == 'GOODBYE 123!' 
assert get_uppercase('12345') == '12345' 
assert get_uppercase('') == ''


print(get_uppercase("Hia Hoo 84!"))