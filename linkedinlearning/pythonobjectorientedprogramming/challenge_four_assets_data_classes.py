from dataclasses import dataclass


@dataclass
class Asset:

    price: float


@dataclass
class Stock(Asset):
    
    ticker: str
    company: str

    def __lt__(self, value):
        return self.price < value.price


@dataclass
class Bond(Asset):

    description: str
    duration: int
    my_yield: float

    def __lt__(self, value):
        return self.my_yield < value.my_yield
    

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