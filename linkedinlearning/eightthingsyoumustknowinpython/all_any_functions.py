import string


input_str = "Hello, World!"

def contains_punctuation(input_str):
    punct = string.punctuation
    ''' Return True if the input_str contains punctuations.
    Return False otherwise'''
    return any(char in punct for char in input_str)


print(contains_punctuation(input_str))