from models.enums import SEAT_TIER
import string

SEAT_ROWS = string.ascii_uppercase[:10]
SEAT_COLS = [i for i in range(1,21)]

RECLINER_ROWS = SEAT_ROWS[:3]
PREMIUM_ROWS = SEAT_ROWS[3:6]

HOLDTIME_MINS = 5

STANDARD_PRICING = {
    SEAT_TIER.REGULAR: 200,
    SEAT_TIER.PREMIUM: 350,
    SEAT_TIER.RECLINER: 500
}