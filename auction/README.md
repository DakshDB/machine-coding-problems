# Auction System 

- User
    - id 
    - name
    - type : Buyer\Seller

- AuctionItem
    - id 
    - seller : User
    - starting_price
    - duration
    - status

- Bid
    - id
    - bidder : User
    - price : int


# Operations 

create_user
create_auction
place_bid
get_auction_status
close_auctio