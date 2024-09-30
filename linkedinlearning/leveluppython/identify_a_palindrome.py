import string


def find_palindrome(text):
    
    text = text.lower() # Convert to lowercase
    print(text)
    
    text_list = list(text) # Convert to list
    #print(text_list)
    
    my_text_list = []
    for char in text_list:
        if str(char) in string.ascii_lowercase:
            my_text_list.append(char)
    #print(my_text_list)

    # Sort the list in reverse order
    reversed_text_list = my_text_list[::-1]
    #print(reversed_text_list)   
    
    if my_text_list == reversed_text_list:
        return True
    else:
        return False


print("This text is palindrome: ", find_palindrome("Go hang a salami - I'm a lasagna hog.")) # True
print("This text is palindrome: ", find_palindrome("Test12345ô!")) # False