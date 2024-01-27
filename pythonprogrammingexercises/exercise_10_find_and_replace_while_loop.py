# Find and Replace using While Loop

def find_and_replace(my_sentence, old_text, new_text):
    
    i=0
    while True:
        if my_sentence[i:i + len(old_text)] == old_text:
            new_sentence = my_sentence.replace(my_sentence[i:i + len(old_text)], new_text)          
            return print(new_sentence)
        else:
            i+=1        
        

find_and_replace("This is her dog, his name is Doggy.", "her", "our")
find_and_replace("This is her dog, his name is Doggy.", "Doggy", "DOGGY")