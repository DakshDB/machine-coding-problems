
from datetime import datetime


class Member:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email


class Book:
    def __init__(self, title: str, isbn: str, author: str):
        self.title = title
        self.isbn = isbn
        self.author = author

class BookCopy:
    def __init__(self, isbn: str, barcode: str):
        self.isbn = isbn
        self.barcode = barcode
    
    def to_dict(self):
        return {
            "isbn": self.isbn,
            "barcode": self.barcode
        }

class Loan:
    def __init__(self, id: str, barcode: str, loan_date: datetime, member_id: str, book_copy: BookCopy):
        self.id = id
        self.barcode = barcode
        self.loan_date = loan_date
        self.member_id = member_id
        self.book_copy = book_copy
    
