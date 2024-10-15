class Book:

    def __init__(self, title, price, discount):
        self.title = title
        self.price = price
        self.discount = discount

    def get_price(self):
        return self.price
    
    def get_discounted_price(self):
        return self.price - self.discount


book_one = Book("My Book", 5.12345, 0.2)
book_two = Book(title="My Second Book", price=20.00, discount=0.5)


# This will print the title of the book one.
print("This is title of book one:", book_one.title)
# This will print the price of the book one.
print("This is price of book one:", book_one.get_price())
### ROUNDING DECIMALS
# This will print the price of the book one rounded to 4 and 5 decimals.
print("The book one price rounded to 4 decimals:", round(book_one.get_price(), 4))
print("The book one price rounded to 5 decimals:", "{:.5f}".format(book_one.get_price()))
# This will print the discounted price of the book one.
print("This is discounted price of book one:", book_one.get_discounted_price())
# This will print the title of the book two.
print("This is title of book two:", book_two.title)