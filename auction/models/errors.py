
class AuctionExceptions(Exception):
    pass

class AuctionNotFound(AuctionExceptions):
    pass

class BidIsClosed(AuctionExceptions):
    pass

class SellerCantBuy(AuctionExceptions):
    pass


class BidShouldBeGreaterThanLastBid(AuctionExceptions):
    pass


# ----- #
class UserExceptions(Exception):
    pass

class SellerNotFound(UserExceptions):
    pass

class BuyerNotFound(UserExceptions):
    pass

class UserNotAllowedToCreateAuction(UserExceptions):
    pass

class UserNotAllowedToBid(UserExceptions):
    pass