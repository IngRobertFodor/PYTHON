from collections import Counter


def count_words(text_file):

    file = open(text_file, "r")
    
    words_list = []
    for line in file:
        line = file.readline()
        #print(line)
        words = list(line.split())
        for word in words:
            # Upper and Lower Case words are considered the same words.
            word = word.lower()
            words_list.append(word)
    print(words_list)
    print("File has:", len(words_list), "words.")
    print()
    
    words_counter = Counter(words_list)
    words_counter = dict(words_counter)
    print(words_counter)
    print()

    word_occurencies_counted = list(words_counter.values())
    word_occurencies_counted.sort(reverse=True) 
    #print(word_occurencies_counted)
    print("Top 10 most common words in the file:")
    for key, value in words_counter.items():
        if value in word_occurencies_counted[0:10]:
            print(key, ":", value)
    print()

    file.close()
     
    return print("File read successfully.")


count_words("william_shakespeare_wiki.txt")
