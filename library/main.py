from time import sleep
from datetime import time
from models.models import Member
from core.book_loan import BookLoan
from models.models import BookCopy
from models.models import Book
if __name__ == "__main__":

    print("Welcome to Library")
    
    member = Member("1", name="DB", email="db22@g.com")

    book1 = Book("B1","b1", "DB")
    bookCopy1 = BookCopy(book1.isbn, "barcode1")
    bookCopy2 = BookCopy(book1.isbn, "barcode2")

    book_loan = BookLoan(books=[book1], bookCopies=[bookCopy1, bookCopy2])

    # Get Available Copies
    print(book_loan.get_available_copies(book1.isbn))    

    # Borrow a book
    loan = book_loan.borrow_book(member_id=member.id, isbn=book1.isbn)
    print(loan.id)

    # Get Available Copies
    print(book_loan.get_available_copies(book1.isbn))   

    # Return Book 
    fine = book_loan.return_book(loan.barcode)
    print(f"Fine to pay for loan {loan.id} is {fine}")

    # Get Available Copies
    print(book_loan.get_available_copies(book1.isbn))   

    # Borrow Books
    loan1 = book_loan.borrow_book(member_id=member.id, isbn=book1.isbn)
    loan2 = book_loan.borrow_book(member_id=member.id, isbn=book1.isbn)
    # loan3 = book_loan.borrow_book(member_id=member.id, isbn=book1.isbn)

    # Return 
    fine = book_loan.return_book(loan1.barcode)
    print(f"Fine to pay for loan {loan.id} is {fine}")

    fine = book_loan.return_book(loan1.barcode)
    print(f"Fine to pay for loan {loan.id} is {fine}")

    



