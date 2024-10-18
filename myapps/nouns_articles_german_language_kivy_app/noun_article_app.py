from kivy.app import App # type: ignore
from kivy.uix.label import Label # type: ignore
from kivy.uix.button import Button # type: ignore
from kivy.uix.boxlayout import BoxLayout # type: ignore
from kivy.uix.popup import Popup # type: ignore
from kivy.clock import Clock # type: ignore
from PyPDF2 import PdfReader # type: ignore
import random


# Define the app class.
class MyPDFApp(App):

    def __init__(self, **kwargs):
        super(MyPDFApp, self).__init__(**kwargs)
        self.correct_guesses = 0
        self.incorrect_guesses = 0

    def read_pdf(self, file_path):
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            # Declare nouns as a global variable.
            global nouns
            nouns = []
            for page_number in range(len(reader.pages)):
                page = reader.pages[page_number]
                text = page.extract_text()
                lines = text.split("\n")
                for line in lines:
                    if line.startswith("der") or line.startswith("die") or line.startswith("das"):
                        article, noun = line.split()[0:2]
                        nouns.append((article, noun))
            # Declare random_noun as a global variable.
            global random_noun
            random_noun = random.choice(nouns)
        return random_noun        

    def show_feedback(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()
        # Change color of popup to light yellow and text color to grey.
        popup.background_color = (1, 1, 0.5, 1)
        popup.content.color = (0.5, 0.5, 0.5, 1)
        return popup

    def build(self):
        # Open PDF file and choose a random noun.
        random_noun = self.read_pdf("noun_article_app.pdf")
        
        # Define the app layout.
        layout = BoxLayout(orientation='vertical')
        
        # Display the question to the user about the article of the noun.
        label = Label(text=f"What is the article of the noun: {random_noun[1]}?")
        layout.add_widget(label)
        # Change color of the question to white and text in bold.
        label.color = (1, 1, 1, 1)
        label.bold = True
                       
        # Three Buttons for the user to make a guess: der, die, das.
        # Der button.
        der_button = Button(text="der")
        der_button.bind(on_press=lambda _: on_guess("der"))
        layout.add_widget(der_button)
        # Die button.
        die_button = Button(text="die")
        die_button.bind(on_press=lambda _: on_guess("die"))
        layout.add_widget(die_button)
        # Das button.
        das_button = Button(text="das")
        das_button.bind(on_press=lambda _: on_guess("das"))
        layout.add_widget(das_button)
        
        # Button for the user to stop the game.
        button = Button(text="Click to Stop")
        button.bind(on_press=lambda _: stop())
        layout.add_widget(button)
        # Change color of "Click to Stop" button to azure blue and text color to green.
        button.background_color = (0, 0.5, 1, 1)
        button.color = (0, 1, 0, 1)

        # Define the functions for the buttons.

        # Function to check the user's guess.
        def on_guess(article):
            # Declare random_noun as a global variable.
            global random_noun
            if random_noun[0] == article:
                self.show_feedback("Your answer:", "CORRECT!")
                self.correct_guesses += 1
                # Find a new random noun.
                random_noun = random.choice(nouns)
                label.text = f"What is the article of the noun: {random_noun[1]}?"
            else:
                self.show_feedback("Your answer:", f"INCORRECT! The correct article is: {random_noun[0]}")
                self.incorrect_guesses += 1
            return
        
        # Function to stop the game.
        def stop():
            total_guesses = self.correct_guesses + self.incorrect_guesses
            if total_guesses > 0:
                accuracy = (self.correct_guesses / total_guesses) * 100
            else:
                accuracy = 0
            stats_message = (f"Correct guesses: {self.correct_guesses}\n"
                             f"Incorrect guesses: {self.incorrect_guesses}\n"
                             f"Score: {accuracy:.2f}%")
            self.show_feedback("Statistics", stats_message)
            # Delay the app stop to allow the popup to be read.
            Clock.schedule_once(lambda dt: App.get_running_app().stop(), 5)
            return
        
        return layout

        
if __name__ == '__main__':
    MyPDFApp().run()