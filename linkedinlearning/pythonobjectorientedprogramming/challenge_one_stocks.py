class Stock:
    
    def __init__(self, ticker, price, company):
        self.ticker = ticker
        self.price = price
        self.company = company

    def get_description(self):
        print(self.ticker +": " + self.company + " -- $" + str(self.price))
        return

    
msft = Stock("MSFT", 342.0, "Microsoft Corp")
goog = Stock("GOOG", 135.0, "Google Inc")
meta = Stock("META", 275.0, "Meta Platforms Inc")
amzn = Stock("AMZN", 135.0, "Amazon Inc")

msft.get_description()
goog.get_description()
meta.get_description()
amzn.get_description()