

class BookLoanExeception(Exception):
    pass


class BookNotFound(BookLoanExeception):
    pass

class NoCopyAvailable(BookLoanExeception):
    pass

class MaxLoanPerMember(BookLoanExeception):
    pass

class MaxFineDueForNewLoan(BookLoanExeception):
    pass

class BarcodeNotFoundInLoan(BookLoanExeception):
    pass