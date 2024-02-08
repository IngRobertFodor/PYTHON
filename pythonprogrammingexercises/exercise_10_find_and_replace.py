# Find and Replace

my_sentence = "This is her dog, his name is Doggy."

def find_and_replace(my_sentence, old_text, new_text):
    
    print("This is original sentence:", my_sentence)
    my_sentence_list = my_sentence.split()
    word_index = my_sentence_list.index(old_text)
    my_sentence_list[word_index] = new_text
    new_sentence = " ".join(my_sentence_list)
    return new_sentence


result = find_and_replace(my_sentence, "her", "our")
print(result)