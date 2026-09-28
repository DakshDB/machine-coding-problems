class FoodDeliveryAppExceptions(Exception):
    pass


class InsufficientInventory(FoodDeliveryAppExceptions):
    pass

class UserNotFound(FoodDeliveryAppExceptions):
    pass

class OrderNotFound(FoodDeliveryAppExceptions):
    pass    

class RestaurantNotFound(FoodDeliveryAppExceptions):
    pass

class OrderNotInStatusToBePicked(FoodDeliveryAppExceptions):
    pass

class NoDeliveryPartnerAvailable(FoodDeliveryAppExceptions):
    pass

class OrderStatusCantBeUpdated(FoodDeliveryAppExceptions):
    pass