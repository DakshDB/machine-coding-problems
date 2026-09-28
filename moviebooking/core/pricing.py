

from models.constants import STANDARD_PRICING
from models.models import Seat
from models.models import Show


class PricingStategy:

    def __init__(self):
        pass

    def calculate_price(self, show: Show, seats: list[Seat]):
        pass

class StandardPricing(PricingStategy):

    def __init__(self):
        super().__init__()

    def calculate_price(self, show: Show, seats: list[Seat]):
        price = 0
        for seat in seats:
            seat_price = STANDARD_PRICING[seat.tier]
            price += seat_price

        if show.start_time.hour < 17:
            price *= 0.75
        
        if show.start_time.isoweekday() in [6,7]:
            price *= 1.25

        return price
            

