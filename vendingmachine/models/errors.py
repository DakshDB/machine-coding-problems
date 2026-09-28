class DenominationError(Exception):
    pass

class VendingError(Exception):
    pass

class InvalidDenomination(DenominationError):
    pass

class InvalidState(VendingError):
    pass 