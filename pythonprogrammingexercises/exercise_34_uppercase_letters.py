import string


# Uppercase Letters

def get_uppercase(my_text):
    
    for character in my_text:
        if character in string.ascii_lowercase:
            character_index_l = string.ascii_lowercase.index(character)
            #print(character_index_l)
            #print(string.ascii_lowercase[character_index_l])
            my_text = my_text.replace(character, string.ascii_uppercase[character_index_l])
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