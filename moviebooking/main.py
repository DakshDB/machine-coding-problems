from core.booking import Booking
from datetime import datetime
from models.constants import SEAT_COLS
from models.models import Screen
from models.models import Show

if __name__ == "__main__":

    print("Welcome to Movie Booking Window")

    screen1 = Screen("1")
    show1 = Show("1", "Movie", screen1, datetime.now() )

    booking_core = Booking([show1])

    print(booking_core.get_available_seats(show1.id))

    hold = booking_core.hold_seats(show1.id, ['C2', 'F3'])
    booking_core.cancel_hold(hold.id)
    hold2 = booking_core.hold_seats(show1.id, ['C2', 'F3'])


    print(booking_core.get_available_seats(show1.id))

    price = booking_core.confirm_booking(hold.id)
    print(f"Price for ticket {price}")
