
from datetime import timedelta
from models.constants import HOLDTIME_MINS
from datetime import datetime
from models.models import Hold
from collections import defaultdict
from models.models import Show
from core.pricing import PricingStategy, StandardPricing

class Booking():

    def __init__(self, shows: list[Show], pricing_strategry: PricingStategy = StandardPricing):
        self.pricing_strategry = pricing_strategry()

        self.holds: dict[str, Hold] = defaultdict()
        self.shows: dict[str, Show] = defaultdict()
        for show in shows:
            self.shows[show.id] = show

    def get_available_seats(self, show_id):
        show = self.shows[show_id]
        show.refresh_holds()
        return show.available_seats


    def hold_seats(self, show_id, seat_ids):
        show = self.shows[show_id]

        hold = show.hold_seats(seat_ids)

        self.holds[hold.id] = hold
        return hold

    def confirm_booking(self, hold_id):
        hold = self.holds[hold_id]

        # Check if Hold is not expired
        if datetime.now() - hold.hold_timestamp > timedelta(minutes=HOLDTIME_MINS):
            raise Exception("Hold Expired")

        show = self.shows[hold.show_id]
        seats = show.book_seats(seat_ids=hold.seat_ids)
        price = self.pricing_strategry.calculate_price(show, seats)
        return price


    def cancel_hold(self, hold_id):
        hold = self.holds[hold_id]
        show = self.shows[hold.show_id]
        show.cancel_holded_seats(hold.seat_ids)
        return