# DATA CLASSES
# from Python 3.7
# including @dataclass decorator
from dataclasses import dataclass


@dataclass(frozen=True)
class Book:

    title: str
    author: str
    pages: int
    price: float


b1 = Book("War and Peace", "Leo Tolstoy", 455, 39.95)
b2 = Book("The Catcher in the Rye", "JD Salinger", 100, 29.95)


print(b1)
print(b2)
print(b1.title)
print(b1 == b2)
print(b1.price > b2.price)