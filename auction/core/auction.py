

from asyncio import Server
from models.errors import BidIsClosed
from uuid import uuid4
from models.errors import AuctionNotFound
from models.errors import UserNotAllowedToBid
from models.errors import BuyerNotFound
from models.models import AuctionItemStatus
from datetime import timedelta
from datetime import datetime
from models.errors import UserNotAllowedToCreateAuction
from models.models import UserType
from models.errors import SellerNotFound
import threading
from models.models import Bid
from models.models import AuctionItem
from models.models import User
class Auction:

    def __init__(self):
        
        self.lock = threading.RLock()

        self.users: dict[str, User] = {}
        self.auctionItems: dict[str, AuctionItem] = {}
        self.bids: dict[str, Bid] = {}

    def create_user(self, user_id, name, type) -> User:
        with self.lock:
            user = User(
                id=user_id,
                name=name,
                type=type
            )
            self.users[user_id] = user
            return user

    def create_auction(self, auction_id:str, seller_id: str, item_name: str, starting_price: int, duration_mins: int) -> AuctionItem:

        seller = self.users.get(seller_id, None)
        if seller is None: 
            raise SellerNotFound()    
        
        if seller.type != UserType.SELLER:
            raise UserNotAllowedToCreateAuction()

        with self.lock:
            auction_item = AuctionItem(
                id=auction_id,
                seller=seller,
                starting_price=starting_price,
                end_time=datetime.now() + timedelta(minutes=duration_mins),
                status=AuctionItemStatus.ACTIVE
            )
            self.auctionItems[auction_id] = auction_item
            return auction_item

    def _if_auction_active(self, auction_id, current_time):
        with self.lock:
            auction = self.auctionItems.get(auction_id, None)
            if auction is None:
                raise AuctionNotFound()
            
            if auction.status != AuctionItemStatus.ACTIVE:
                raise BidIsClosed()

            if current_time is None:
                current_time = datetime.now()
            if current_time > auction.end_time:
                auction.status = AuctionItemStatus.CLOSED
                raise BidIsClosed()
            
            

    def place_bid(self, buyer_id, auction_id, amount, current_time=None) -> bool:
        
        self._if_auction_active(auction_id, current_time)

        with self.lock:
            buyer = self.users.get(buyer_id, None)
            if buyer is None:
                raise BuyerNotFound()

            if buyer.type != UserType.BUYER:
                raise UserNotAllowedToBid()
            
            auction = self.auctionItems.get(auction_id, None)
            if auction is None:
                raise AuctionNotFound()

            highest_bid = auction.highest_bid

            if highest_bid:
                if amount > highest_bid.price:
                    highest_bid = Bid(
                        id=str(uuid4()),
                        bidder=buyer,
                        price=amount
                    )
                else:
                    return False
            else:
                if amount > auction.starting_price:
                    highest_bid = Bid(
                        id=str(uuid4()),
                        bidder=buyer,
                        price=amount
                    )
                else:
                    return False
            
            auction.highest_bid = highest_bid
            return True
    
    
    def get_auction_status(self, auction_id: str) -> dict:
        with self.lock:
            auction = self.auctionItems.get(auction_id, None)
            if auction is None:
                raise AuctionNotFound()
            
            highest_bid_amount = None
            highest_bidder = None

            highest_bid = auction.highest_bid
            if highest_bid:
                highest_bid_amount = highest_bid.price
                highest_bidder = highest_bid.bidder.name
            
            return {
                "id": auction.id,
                "status": auction.status,
                "highest_bid_amount": highest_bid_amount,
                "highest_bidder": highest_bidder
            }

    def close_auction(self, auction_id) -> str|None:
        with self.lock:
            auction = self.auctionItems.get(auction_id, None)
            if auction is None:
                raise AuctionNotFound()

            auction.status = AuctionItemStatus.CLOSED

            if auction.highest_bid is None:
                return None
            
            return auction.highest_bid.bidder.id