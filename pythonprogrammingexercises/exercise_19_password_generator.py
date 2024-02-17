import random
import string


# Password Generator

possible_characters = list(string.printable)
#print("All possible password characters.")
#print(possible_characters)
random.shuffle(possible_characters)
#print(possible_characters)
#print()

special_characters = "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+"
special_characters = list(special_characters)
#print("Special characters for password.")
#print(special_characters)
#print()

def generate_password(password_length):
    
    if password_length < 12:
        password_length = 12
    else:
        password_length = password_length
    
    my_upper_character = random.choice(string.ascii_uppercase)
    my_lower_character = random.choice(string.ascii_lowercase)
    my_digit = random.choice(string.digits)
    my_special_character = random.choice(special_characters)
    my_default_chracters = list(my_upper_character + my_lower_character + my_digit + my_special_character)
    #print("Default characters for password.")    
    #print(my_default_chracters)
    #print()
    
    my_other_characters_length = password_length - len(my_default_chracters)
    my_other_characters = possible_characters[0:my_other_characters_length]
    #print("Other characters for password.")
    #print(my_other_characters)
    #print()
    
    password = list(my_default_chracters + my_other_characters)
    random.shuffle(password)
    return password


# Asserts
assert len(generate_password(8)) == 12
pw = generate_password(14)
assert len(pw) == 14 
hasLowercase = False 
hasUppercase = False 
hasNumber = False 
hasSpecial = False 
for character in pw: 
    if character in string.ascii_lowercase: 
        hasLowercase = True 
    if character in string.ascii_uppercase: 
        hasUppercase = True 
    if character in string.digits: 
        hasNumber = True 
    if character in special_characters: 
        hasSpecial = True 
assert hasLowercase and hasUppercase and hasNumber and hasSpecial


result_one = generate_password(10)
print(result_one)
print()
result_two = generate_password(15)
print(result_two)