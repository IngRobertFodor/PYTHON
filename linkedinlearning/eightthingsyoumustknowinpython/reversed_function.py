# reversed()

test_cases = [
   "sagas",
   "Radar",
   "Was it a cat I saw?",
   "Eva, can I see bees in a cave",
   "Red rum, sir, is MURDER!!",
   "This should not not work",
   "radars"
]

def is_palindrome(words):
    '''Palindromes are case insensitive, so both radar and Radar are valid'''

    #print(words)
    new_words = words.replace(".", "").replace(",", "").replace("?", "").replace("!", "").replace(" ", "")
    #print(new_words)
    lower_words = new_words.lower()
    #print(lower_words)
    
    reversed_text = "".join(reversed(lower_words))
    #print(reversed_text)
    
    if lower_words == reversed_text:
        return True
    else:
        return False


for item in test_cases:
    print(is_palindrome(item))