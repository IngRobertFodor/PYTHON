class Asset:

    def __init__(self, price):
        self.price = price


class Stock(Asset):
    
    def __init__(self, ticker, price, company):
        super().__init__(price)
        self.ticker = ticker
        self.company = company

    def __str__(self):
        return f"{self.ticker}: {self.company} -- ${self.price}"

    def __ge__(self, value):
        if isinstance(value, Stock):
            return self.price >= value.price
        else:
            raise ValueError("Can't compare.")
    
    def __lt__(self, value):
        if isinstance(value, Stock):
            return self.price < value.price
        else:
            raise ValueError("Can't compare.")


class Bond(Asset):

    def __init__(self, price, description, duration, my_yield):
        super().__init__(price)
        self.description = description
        self.duration = duration
        self.my_yield = my_yield

    def __str__(self):
        return f"{self.description}:  {self.duration}yr : ${self.price} : {self.my_yield}%"
    
    def __ge__(self, value):
        if isinstance(value, Bond):
            return self.my_yield >= value.my_yield
        else:
            raise ValueError("Can't compare.")
    
    def __lt__(self, value):
        if isinstance(value, Bond):
            return self.my_yield < value.my_yield
        else:
            raise ValueError("Can't compare.")
    

msft = Stock("MSFT", 342.0, "Microsoft Corp")
goog = Stock("GOOG", 135.0, "Google Inc")
meta = Stock("META", 275.0, "Meta Platforms Inc")
amzn = Stock("AMZN", 135.0, "Amazon Inc")
my_stocks = [msft, goog, meta, amzn]
my_stocks.sort()

us30yr = Bond(95.31, "30 Year US Treasury", 30, 4.38)
us10yr = Bond(96.70, "10 Year US Treasury", 10, 4.28)
us5yr = Bond(98.65, "5 Year US Treasury", 5, 4.43)
us2yr = Bond(99.57, "2 Year US Treasury", 2, 4.98)
my_bonds = [us30yr, us10yr, us5yr, us2yr]
my_bonds.sort()


print("Stocks")
for stock in my_stocks:
    print(stock)
print()
print("Bonds")
for bond in my_bonds:
    print(bond)