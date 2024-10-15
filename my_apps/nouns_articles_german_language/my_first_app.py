# OPEN PDF PURPOSES
from PyPDF2 import PdfReader # type: ignore
import random


##########################################################################################
def read_pdf(file_path):
    
    with open("common_german_nouns.pdf", "rb") as file: # Open in binary read mode.
        
        reader = PdfReader(file)
        line_list = []
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            text = page.extract_text()
            lines = text.split("\n")
            for line in lines:
                if line.startswith("der") or line.startswith("die") or line.startswith("das"): # Check if the line starts with "der", "die" or "das".
                    article_noun = line.split()[0:2] # Print the first two words of the line.
                    print(article_noun)
                    line_list.append(article_noun)
                        
        return line_list


##########################################################################################
def find_nouns(nouns):

    random_item = random.choice(nouns)
    print(random_item)
    
    return random_item


##########################################################################################
def user_guess(noun):

    print("What is the article of the noun:     " + noun[1] + "?")
    guess = input("Type your guess, 'der', 'die' or 'das': ").lower()
    article = noun[0]
    if guess in ["der", "die", "das"] and guess == article:
        print("Correct!")
    else:
        print("Incorrect!")
        print("The correct answer is:     " + article)
    return


##########################################################################################
# Path to the PDF file.
file_path = "path_to_your_pdf_file.pdf"
# Read the PDF file.
read_pdf = read_pdf(file_path)
print()
# Find the noun.
noun = find_nouns(read_pdf)
print()
# User guesses the article of the noun.
user_guess(noun)