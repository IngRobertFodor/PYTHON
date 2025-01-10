    ### This is CREATING CLASS (Book).

class Book:

    def __init__(self, title, price, discount):
        self.title = title
        self.price = price
        self.discount = discount

    def get_price(self):
        return self.price
    
    def get_discounted_price(self):
        return self.price - self.discount


    ### This is CREATING INSTANCE OF Book CLASS (book_one and book_two).

book_one = Book("My Book", 5.12345, 0.2)
book_two = Book(title="My Second Book", price=20.00, discount=0.5)


# This will print the type of the book_one.
# Output: <class '__main__.Book'>.
print("The type of book_one is:", type(book_one))

# This will check if book_one is an instance of Book class.
# Output: True.
print("Is book_one an instance of Book class?", isinstance(book_one, Book))

# This will print the title of the book_one.
print("This is title of book_one:", book_one.title)
# This will print the price of the book_one.
print("This is price of book_one:", book_one.get_price())
print("This is price of book_one:", book_one.price)

    ## ROUNDING DECIMALS
# This will print the price of the book_one rounded to 4 and 5 decimals.
print("The book_one price rounded to 4 decimals:", round(book_one.get_price(), 4))
print("The book_one price rounded to 5 decimals:", "{:.5f}".format(book_one.get_price()))

# This will print the title of the book_two.
print("This is title of book_two:", book_two.title)
print()


    ### This is another example of creating a class (Newspaper).

class Newspaper():
    
    def __init__(self, title):
        self.title = title


    ### and an instance of the Newspaper class (newspaper_one).

newspaper_one = Newspaper("The New York Times")


# This will print the type of the newspaper_one.
# Output: <class '__main__.Newspaper'>.
print("The type of newspaper_one is:", type(newspaper_one))

# This will check if newspaper_one is an instance of Book class.
# Output: False.
print("Is newspaper_one an instance of Book class?", isinstance(newspaper_one, Book))

# This will print the title of the newspaper_one.
print("This is title of newspaper_one:", newspaper_one.title)
print()