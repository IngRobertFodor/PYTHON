import string


# Title Case

x = list(string.printable)
#print("All characters:")
#print(x)

lowercase = list(string.ascii_lowercase)
#print("Lowercase characters:")
#print(lowercase)

uppercase = list(string.ascii_uppercase)
#print("Uppercase characters:")
#print(uppercase)

other_characters_from_x = []
for ch in x:
     if ch in lowercase or ch in uppercase:
          continue
     else:
          other_characters_from_x.append(ch)
#print("Other characters from x:")
#print(other_characters_from_x)

def title_case(my_text):
    
    characters_list = []
    for character in my_text:
        characters_list.append(character)
    #print(characters_list)
    
    # This makes all characters lowercase + special characters.
    for i in range(0, len(characters_list)):
        if characters_list[i] in other_characters_from_x:
             continue
        else:
          characters_list[i] = characters_list[i].lower()
    #print(characters_list)
    
    # This makes the second part of the exercise.
    for j in range(0, len(characters_list)):
        if characters_list[0] in lowercase:
            characters_list[0] = characters_list[0].upper()
        elif characters_list[0] in other_characters_from_x:
             continue
        elif characters_list[j] in lowercase and characters_list[j-1] in other_characters_from_x:
            characters_list[j] = characters_list[j].upper()
        elif characters_list[j] in lowercase and characters_list[j-1] in lowercase:
            continue
    print(characters_list)
     
    string_from_characters_list = "".join(characters_list)            
    
    return string_from_characters_list


# Asserts
assert title_case('Hello, world!') == 'Hello, World!' 
assert title_case('HELLO') == 'Hello' 
assert title_case('hello') == 'Hello'
assert title_case('hElLo') == 'Hello' 
assert title_case('') == '' 
assert title_case('abc123xyz') == 'Abc123Xyz' 
assert title_case('cat dog RAT') == 'Cat Dog Rat' 
assert title_case('cat,dog,RAT') == 'Cat,Dog,Rat'


print()
print(title_case("Hello, 5world!"))