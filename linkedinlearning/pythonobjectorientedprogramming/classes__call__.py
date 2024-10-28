class Book:

    def __init__(self, title, author, price):
        super().__init__()
        self.title = title
        self.author = author
        self.price = price

    def __str__(self):
        return f"{self.title} by {self.author} for: {self.price}$."
    
        ## __call__
    # __call__ method is used to make an object callable like a function.
    def __call__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price


book_one = Book("The Alchemist", "Paulo Coelho", 10.0)
print(book_one)
# Output: The Alchemist by Paulo Coelho for: 10.0$.
book_one("The Alchemist_Test", "Paulo Coelho", 11.0)
print(book_one)
# Output: The Alchemist_Test by Paulo Coelho for: 11.0$.