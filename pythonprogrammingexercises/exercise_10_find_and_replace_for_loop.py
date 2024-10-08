# Find and Replace using For Loop

def find_and_replace(my_sentence, old_text, new_text):
    
    print("Original sentence was:", my_sentence)
    
    for i in range(0, len(my_sentence)):
        if my_sentence[i:i + len(old_text)] == old_text:
            print("Old text was:", old_text)
            new_sentence = my_sentence.replace(my_sentence[i:i + len(old_text)], new_text)
            return new_sentence


result_one = find_and_replace("This is her dog, his name is Doggy.", "her", "our")
print(result_one)
result_two = find_and_replace("This is her dog, his name is Doggy.", "Doggy", "DOGGY")
print(result_two)