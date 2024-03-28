import string


# Reverse String

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

def reverse_string(my_text):
    
    characters_list = []
    for character in my_text:
        characters_list.append(character)
    #print(characters_list)
    
    characters_list_reversed = []
    for item in range((len(characters_list)-1),-1,-1):
        characters_list_reversed.append(characters_list[item])             
    #print(characters_list_reversed)
        
    string_from_characters_list_reversed = "".join(characters_list_reversed)            
    
    return string_from_characters_list_reversed


# Asserts
assert reverse_string('Hello') == 'olleH' 
assert reverse_string('') == '' 
assert reverse_string('aaazzz') == 'zzzaaa' 
assert reverse_string('xxxx') == 'xxxx'


print()
print(reverse_string("Hello !"))