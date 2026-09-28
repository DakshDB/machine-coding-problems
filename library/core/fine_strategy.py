from models.constants import CURRENT_TIME_OFFSET
from models.constants import MAX_FINE_PER_LOAN
from models.constants import FINE_PER_DAY
from models.constants import LOAN_PERIOD_DAYS
from datetime import timedelta
from datetime import datetime
class FineStrategy:

    def __init__(self):
        pass

    def calculate_fine(self, book_loan_date: datetime):
        pass

class StandardFineStrategy(FineStrategy):
    
    def __init__(self):
        super().__init__()

    def calculate_fine(self, book_loan_date: datetime):
        # Apply Offset 
        current_time = datetime.now() + CURRENT_TIME_OFFSET

        # Get Loan Duration 
        loan_duration = current_time - book_loan_date
        if loan_duration <= timedelta(days=LOAN_PERIOD_DAYS):
            return 0

        fine_days = loan_duration.days - LOAN_PERIOD_DAYS
        fine = fine_days * FINE_PER_DAY
        fine = min(fine, MAX_FINE_PER_LOAN)
        return fine


        

