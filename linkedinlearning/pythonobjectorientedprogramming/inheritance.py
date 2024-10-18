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


b1 = Book("Brave New World", "Aldous Huxley", 311, 29.11)
m1 = Magazine("Scientific American", "Springer Nature", 5.99, "Monthly")
n1 = Newspaper("NY Times", "New York Times Company", 6.0, "Daily")


print(b1.author)
print(n1.publisher)
print(b1.price, m1.price, n1.price)
print(round(b1.price, 2), m1.price, "{:.2f}".format(n1.price))