class Book:

    def __init__(self, title, author, price):
        super().__init__()
        self.title = title
        self.author = author
        self.price = price

        ## __eq__
    # __eq__ method checks for equality between two objects.
    # eq = EQUAL
    def __eq__(self, value):
        if  isinstance(value, Book):
            return self.title == value.title and self.author == value.author and self.price == value.price
        else:
            return ValueError("Can't compare book to non-book type.")
    
        ## __ge__
    # __ge__ for comparing greater than or equal to another object.
    # ge = GREATER THAN OR EQUAL TO
    def __ge__(self, value):
        if isinstance(value, Book):
            return self.price >= value.price
        else:
            return ValueError("Can't compare book to non-book type.")

        ## __lt__    
    # __lt__ for comparing less than another object.
    # lt = LESS THAN
    def __lt__(self, value):
        if isinstance(value, Book):
            return self.price < value.price
        else:
            raise ValueError("Can't compare book to non-book type.")


## There are comparison methods like: __gt__, __le__, __ne__, etc.


b1 = Book("War and Peace", "Leo Tolstoy", 39.95)
b2 = Book("The Catcher in the Rye", "JD Salinger", 29.95)
b3 = Book("War and Peace", "Leo Tolstoy", 39.95)
b4 = Book("To Kill a Mockingbird", "Harper Lee", 24.95)


# Check for equality.
print("b1 is the same as b3: ", end="")
print(b1 == b3)
# Output: True
print("b1 is the same as b2: ", end="")
print(b1 == b2)
# Output: False
print("b1 is the same as 42: ", end="")
print(b1 == 42)
# Output: ValueError: Can't compare book to non-book type.
print()


# Comparing using __ge__ and __lt__.
print(b2 >= b1)
print(b2 < b1)
print(b3 >= b2)


# Sorted list of books by price.
books = [b1, b2, b3, b4]
books.sort()
print([book.title for book in books])