
from datetime import datetime
from datetime import timedelta
from enum import Enum


class UserType(Enum):

    SELLER = 'seller'
    BUYER = 'buyer'

class AuctionItemStatus(Enum):

    ACTIVE = 'active'
    CLOSED = 'closed'

class User:

    def __init__(self, id: str, name: str, type: UserType):
        self.id = id 
        self.name = name
        self.type = type

class AuctionItem:

    def __init__(self, id: str, seller: User, starting_price: int, end_time: datetime, status: AuctionItemStatus, highest_bid = None):
        self.id = id
        self.seller = seller
        self.starting_price = starting_price
        self.end_time = end_time
        self.status = status
        self.highest_bid = highest_bid

class Bid:
    
    def __init__(self, id: str, bidder: User, price: int):
        self.id = id 
        self.bidder = bidder
        self.price = price

