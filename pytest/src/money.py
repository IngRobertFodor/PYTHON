# Money Management System Exercise
'''
Create a program that can handle money amounts in various currencies (e.g., USD, EUR).
The system should be able to convert between currencies using exchange rates.
You should be able to add these amounts to an e-wallet.
The program should also be able to handle negative exchange rates (e.g., removing from the e-wallet). 
'''


class Money:

    def __init__(self, amount: int, currency: str, exchange_rate: float, base_currency: str):
        self.amount = amount
        self.currency = currency
        self.exchange_rate = exchange_rate
        self.base_currency = base_currency
        
    def convert(self):
        if self.currency != self.base_currency:
            return self.amount * self.exchange_rate
        else:
            return self.amount * 1.0

    def add_to_e_wallet(self):
        e_wallet = 0.0
        e_wallet += self.convert()
        return e_wallet