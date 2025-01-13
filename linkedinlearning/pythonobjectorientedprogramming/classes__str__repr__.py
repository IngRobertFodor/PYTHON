class Book:

    def __init__(self, title, author, price):
        super().__init__()
        self.title = title
        self.author = author
        self.price = price

        ## __str__
    # __str__ function is used to return a user-friendly string representation of the object.
    def __str__(self):
        return f"{self.title} by {self.author} for: {self.price}$."

        ## __repr__
    # __repr__ function is used to return a developer-friendly string representation of the object.
    def __repr__(self):
        return f"title={self.title} by author={self.author} for price={self.price}$."


b1 = Book("War and Peace", "Leo Tolstoy", 39.95)
b2 = Book("The Catcher in the Rye", "JD Salinger", 29.95)


print(b1)
# Output:
# War and Peace by Leo Tolstoy for: 39.95$.
print(b2)
# Output:
# The Catcher in the Rye by JD Salinger for: 29.95$.
print()


# Use str() and repr().
print(str(b1))
# Output:
# War and Peace by Leo Tolstoy for: 39.95$.
print(repr(b2))
# Output:
# title=The Catcher in the Rye by author=JD Salinger for price=29.95$.