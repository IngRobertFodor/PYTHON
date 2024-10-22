class Asset:

    def __init__(self, price):
        self.price = price


class Stock(Asset):
    
    def __init__(self, ticker, price, company):
        super().__init__(price)
        self.ticker = ticker
        self.company = company

    def get_description(self):
        return print(self.ticker + ": " + self.company + " -- $" + str(self.price))


class Bond(Asset):

    def __init__(self, price, description, duration, my_yield):
        super().__init__(price)
        self.description = description
        self.duration = duration
        self.my_yield = my_yield

    def get_description(self):
        return print(self.description + ": " + str(self.duration) + "yr : $" + str(self.price) + " : " + str(self.my_yield) + "%")

    
msft = Stock("MSFT", 342.0, "Microsoft Corp")
goog = Stock("GOOG", 135.0, "Google Inc")
meta = Stock("META", 275.0, "Meta Platforms Inc")
amzn = Stock("AMZN", 135.0, "Amazon Inc")

us30yr = Bond(95.31, "30 Year US Treasury", 30, 4.38)
us10yr = Bond(96.70, "10 Year US Treasury", 10, 4.28)
us5yr = Bond(98.65, "5 Year US Treasury", 5, 4.43)
us2yr = Bond(99.57, "2 Year US Treasury", 2, 4.98)


print("Stocks")
msft.get_description()
goog.get_description()
meta.get_description()
amzn.get_description()
print()
print("Bonds")
us30yr.get_description()
us10yr.get_description()
us5yr.get_description()
us2yr.get_description()