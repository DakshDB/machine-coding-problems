from enum import Enum

class SEAT_TIER(Enum):
    REGULAR = 'regular'
    PREMIUM = 'premium'
    RECLINER = 'recliner'

class SEAT_STATUS(Enum):
    AVAILABLE = 'available'
    BOOKED = 'booked'
    HOLD = 'on_hold'