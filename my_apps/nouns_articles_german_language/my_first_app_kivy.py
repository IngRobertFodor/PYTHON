from kivy.app import App # type: ignore
from kivy.uix.label import Label # type: ignore
from kivy.uix.button import Button # type: ignore
from kivy.uix.boxlayout import BoxLayout # type: ignore
from PyPDF2 import PdfReader # type: ignore
import random


# Define the app class.
class MyPDFApp(App):
    

    def read_pdf(self, file_path):
        
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            nouns = []
            for page_number in range(len(reader.pages)):
                page = reader.pages[page_number]
                text = page.extract_text()
                lines = text.split("\n")
                for line in lines:
                    if line.startswith("der") or line.startswith("die") or line.startswith("das"):
                        article, noun = line.split()[0:2]
                        nouns.append((article, noun))

        return nouns


    def user_guess(self, correct_article):
        
        guess = input("Type your guess, 'DER', 'DIE' or 'DAS': ").lower()
        if guess in ["der", "die", "das"] and guess == correct_article:
            print("Correct!")
            self.stop() # Close the app.
        else:
            print("Incorrect!"), print("The correct answer is: " + correct_article)
            self.stop() # Close the app.

        return


    def build(self):
    # Open PDF file and extract the nouns.
        nouns = self.read_pdf("common_german_nouns.pdf")

        # Find a random noun.
        random_noun = random.choice(nouns)

        # Define the app layout.
        layout = BoxLayout(orientation='vertical')

        # Display the random noun.
        label = Label(text=f"What is the article of the noun: {random_noun[1]}?")
        layout.add_widget(label)

        # Button for the user to make a guess.
        button = Button(text="Click to Guess")
        button.bind(on_press=lambda instance: self.user_guess(random_noun[0]))
        layout.add_widget(button)

        return layout


if __name__ == '__main__':
    MyPDFApp().run()