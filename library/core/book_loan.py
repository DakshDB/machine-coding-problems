


from models.errors import BarcodeNotFoundInLoan
from models.errors import MaxFineDueForNewLoan
from models.constants import MAX_DUE_FINE_FOR_NEW_LOAN
from core.fine_strategy import StandardFineStrategy
from core.fine_strategy import FineStrategy
from models.errors import MaxLoanPerMember
from models.constants import MAX_LOAN_PER_MEMBER
from datetime import datetime
from datetime import date
from uuid import uuid4
from models.errors import NoCopyAvailable
from models.models import Book
from collections import defaultdict
from models.models import BookCopy
from models.models import Loan


class BookLoan:

    def __init__(self, books: list[Book], bookCopies: list[BookCopy], fine_strategy: FineStrategy = StandardFineStrategy):
        
        self.fine_strategy: FineStrategy = fine_strategy()

        self.books: set = set[books]
        self.available_book_copies: dict[str, set] = defaultdict(set)
        
        for bookCopy in bookCopies:
            self.available_book_copies[bookCopy.isbn].add(bookCopy)

        self.member_loans: dict[str, set] = defaultdict(set)
        self.loans: dict[str, Loan] = defaultdict()


    def borrow_book(self, member_id: str, isbn: str) -> Loan:
        
        # Check member existing loans 
        member_loans = self.get_loan_by_member(member_id)
        if len(member_loans) >= MAX_LOAN_PER_MEMBER:
            raise MaxLoanPerMember()
        
        # Check the total fine due for member 
        total_member_fine_due = self._get_fine_by_member(member_id)
        if total_member_fine_due >= MAX_DUE_FINE_FOR_NEW_LOAN:
            raise MaxFineDueForNewLoan()

        # Find the available book copies
        available_copies = self.get_available_copies(isbn)
        if len(available_copies) == 0:
            raise NoCopyAvailable()
        
        copy_to_loan = self.available_book_copies[isbn].pop()

        loan = Loan(
            id=str(uuid4()),
            barcode=copy_to_loan.barcode,
            loan_date=datetime.now(),
            member_id=member_id,
            book_copy=copy_to_loan
        )

        self.member_loans[member_id].add(loan.barcode)
        self.loans[loan.barcode] = loan
        return loan

    def return_book(self, barcode: str) -> int:
        try:
            loan = self.loans.pop(barcode)
        except KeyError:
            raise BarcodeNotFoundInLoan()
        
        # Clear Member Loan
        self.member_loans[loan.member_id].discard(loan.barcode)

        # Add the available book back
        self.available_book_copies[loan.book_copy.isbn].add(loan.book_copy)

        fine = self.fine_strategy.calculate_fine(loan.loan_date)
        return fine 


    def get_available_copies(self, isbn: str) -> list[BookCopy]:
        # Get Available book copies
        books = []

        for book in self.available_book_copies[isbn]:
            books.append(
                book.to_dict()
            )
        return books

    def get_loan_by_member(self, member_id: str) -> list[Loan]:
        return self.member_loans[member_id]

    def _get_fine_by_member(self, member_id:str) -> int:
        member_loans = self.get_loan_by_member(member_id)
        if len(member_loans ) == 0:
            return 0

        total_fine = 0
        for member_loan_barcode in member_loans:
            loan_data = self.loans[member_loan_barcode]
            total_fine += self.fine_strategy.calculate_fine(loan_data.loan_date)

        return total_fine



