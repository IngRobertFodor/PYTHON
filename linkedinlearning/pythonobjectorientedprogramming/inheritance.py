class Publication:

    def __init__(self, title, price):
        self.title = title
        self.price = price


class Periodical(Publication):

    def __init__(self, title, publisher, price, period):
        super().__init__(title, price)        
        self.publisher = publisher
        self.period = period


class Book(Publication):

    def __init__(self, title, author, pages, price):
        super().__init__(title, price)
        self.author = author
        self.pages = pages


class Magazine(Periodical):

    def __init__(self, title, publisher, price, period):
        super().__init__(title, publisher, price, period)
        

class Newspaper(Periodical):

    def __init__(self, title, publisher, price, period):
        super().__init__(title, publisher, price, period)


book_one = Book("Brave New World", "Aldous Huxley", 311, 29.11)
magazine_one = Magazine("Scientific American", "Springer Nature", 5.99, "Monthly")
newspaper_one = Newspaper("NY Times", "New York Times Company", 6.0, "Daily")


print(book_one.author)
print(newspaper_one.publisher)
print(book_one.price, magazine_one.price, newspaper_one.price)
print(round(book_one.price, 2), magazine_one.price, "{:.2f}".format(newspaper_one.price))