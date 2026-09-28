
from models.constants import HOLDTIME_MINS
from uuid import uuid4
from models.constants import RECLINER_ROWS
from models.constants import PREMIUM_ROWS
from models.constants import SEAT_COLS
from models.constants import SEAT_ROWS
from collections import defaultdict
from datetime import timedelta
from datetime import datetime
from models.enums import SEAT_STATUS, SEAT_TIER

class Hold: 
    def __init__(self, id: str, seat_ids: list, show_id, hold_timestamp):
        self.id = id
        self.seat_ids = seat_ids
        self.show_id = show_id
        self.hold_timestamp = hold_timestamp


class Seat:
    
    def __init__(self, id: str, tier: SEAT_TIER, status: SEAT_STATUS):
        self.id = id 
        self.tier = tier
        self.status = status


class Screen: 

    def __init__(self, id: str):
        self.id = id
        self._populate_seats()
    
    def _populate_seats(self):
        self.seats: dict = defaultdict()

        for row in SEAT_ROWS:
            for col in SEAT_COLS:
                self.seats[f"{row}{col}"] = (
                    Seat(id=f"{row}{col}", tier=SEAT_TIER.PREMIUM if row in PREMIUM_ROWS else (SEAT_TIER.RECLINER if row in RECLINER_ROWS else SEAT_TIER.REGULAR), status=SEAT_STATUS.AVAILABLE)
                    )
    
    def book_seat(self, seat_id):
        seat = self.seats[seat_id]
        seat.status = SEAT_STATUS.BOOKED
        return seat



class Show:
    
    def __init__(self, id: str, title: str, screen: Screen, start_time: datetime):
        self.id = id
        self.title = title
        self.screen = screen
        self.start_time = start_time

        
        self.available_seats = set([seat for seat in screen.seats.keys()])
        self.holded_seats: dict[str, datetime] = defaultdict(datetime)

    def hold_seats(self, seat_ids: list[int]):
        # Refresh Holds
        self.refresh_holds()
        
        all_found = True
        for seat_id in seat_ids:
            if seat_id not in self.available_seats:
                all_found = False
        if all_found == False:
            raise Exception("Seats Not Available")

        for seat_id in seat_ids:
            self.holded_seats[seat_id] = datetime.now()
            self.available_seats.discard(seat_id)

        hold = Hold(
            id=str(uuid4()),
            seat_ids=seat_ids,
            show_id=self.id,
            hold_timestamp=datetime.now()
        )
        return hold
        
    def book_seats(self, seat_ids) -> list[Seat]:
        booked_seats = []
        for seat_id in seat_ids:
            # Release the hold 
            self.holded_seats.pop(seat_id)
            seat = self.screen.book_seat(seat_id)
            booked_seats.append(seat)
        
        return booked_seats


    def refresh_holds(self):
        for seat_id, hold_timestamp in list(self.holded_seats.items()):
            if datetime.now() - hold_timestamp > timedelta(minutes=HOLDTIME_MINS):
                # Release the hold
                self.holded_seats.pop(seat_id)
                # Make it available
                self.available_seats.add(seat_id)

    def cancel_holded_seats(self, seat_ids):
        for seat_id in seat_ids:
            # Release the hold
            self.holded_seats.pop(seat_id)
            # Make it available
            self.available_seats.add(seat_id)

