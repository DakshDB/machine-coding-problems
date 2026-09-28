

from models.errors import BidShouldBeGreaterThanLastBid
from models.errors import BidIsClosed
from core.auction import Auction
from models.models import UserType
from uuid import uuid4
from models.models import User
if __name__ == '__main__':

    print("Auction is Here")

    auction = Auction()

    buyer = auction.create_user(
        user_id=str(uuid4()),
        name="buyer",
        type=UserType.BUYER
    )

    seller = auction.create_user(
        user_id=str(uuid4()),
        name="seller",
        type=UserType.SELLER
    )

    auction_item = auction.create_auction(
        auction_id=str(uuid4()),
        seller_id=seller.id,
        item_name="Iphone",
        starting_price=50000,
        duration_mins=5
    )
    print(f"Auction Item = {auction_item.id}")

    bid = auction.place_bid(
        buyer_id=buyer.id,
        auction_id=auction_item.id,
        amount=51000
    )
    print(f"Bid is {bid}")

    bid = auction.place_bid(
        buyer_id=buyer.id,
        auction_id=auction_item.id,
        amount=50100
    )
    print(f"Bid is {bid}")

    bid = auction.place_bid(
        buyer_id=buyer.id,
        auction_id=auction_item.id,
        amount=60100
    )
    print(f"Bid is {bid}")

    print(f"Auction Status\n{auction.get_auction_status(auction_item.id)}")

    print(f"Close Auction \n{auction.close_auction(auction_item.id)}")

    try:
        bid = auction.place_bid(
            buyer_id=buyer.id,
            auction_id=auction_item.id,
            amount=51000
        )
        print(f"Bid is {bid}")
    except BidIsClosed:
        print("Test Case Passed - BidIsClosed")
