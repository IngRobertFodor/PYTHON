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


    ### This is another example of creating a class (Newspaper).

class Newspaper():
    
    def __init__(self, title):
        self.title = title