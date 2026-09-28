from models.errors import *
from models.models import *
from core.food_delivery_core import FoodDeliveryCore

if __name__ == '__main__':

    print("Welcome to Fast Food Delivery")

    food_delivery_core = FoodDeliveryCore()


    user = food_delivery_core.add_user("Daksh")
    print(user.log())

    restaurant = food_delivery_core.add_restaurant(
        name="Swaad",
        menu={
            'Pizza':1,
            'Burger': 1
        }
    )
    print(restaurant.log())

    delivery_partner = food_delivery_core.add_delivery_partner("rider")
    print(delivery_partner.log())

    order = food_delivery_core.place_order(
        user_id=user.user_id,
        restaurant_id=restaurant.restaurant_id,
        items={
            'Pizza': 1
        }
    )
    print(order.log())


    ## Test 1 - Place order for not available item
    try:
        order = food_delivery_core.place_order(
            user_id=user.user_id,
            restaurant_id=restaurant.restaurant_id,
            items={
                'BURGER': 1
            }
        )
    except InsufficientInventory:
        print("Test Validated | Error - InsufficientInventory")

    # Test 2 - Exhaused Items
    try: 
        order = food_delivery_core.place_order(
            user_id=user.user_id,
            restaurant_id=restaurant.restaurant_id,
            items={
                'Pizza': 1
            }
        )
    except InsufficientInventory:
        print("Test Validated | Error - InsufficientInventory")

    
    # Test 3 -  Prematurate Status Update
    try:
        order = food_delivery_core.update_order_status(
            order_id=order.order_id,
            status=OrderStatus.DELIVERED
        )
    except OrderStatusCantBeUpdated:
        print("Test Validated | Error - OrderStatusCantBeUpdated")

    order2 = food_delivery_core.place_order(
        user_id=user.user_id,
        restaurant_id=restaurant.restaurant_id,
        items={
            'Burger': 1
        }
    )

    assigned_partner = food_delivery_core.assign_delivery_partner(
        order_id=order.order_id
    )
    print(assigned_partner.log())

    # Test 4 - Order already picked
    try: 
        assigned_partner = food_delivery_core.assign_delivery_partner(
            order_id=order.order_id
        )
    except OrderNotInStatusToBePicked:
        print("Test Validated | Error - OrderNotInStatusToBePicked")

    # Test 5 - Assign delivery Partner
    try: 
        assigned_partner = food_delivery_core.assign_delivery_partner(
            order_id=order2.order_id
        )
    except NoDeliveryPartnerAvailable:
        print("Test Validated | Error - NoDeliveryPartnerAvailable")
    
    order = food_delivery_core.update_order_status(
        order_id=order.order_id,
        status=OrderStatus.DELIVERED
    )
    print(order.log())

    # Test 6 - Order 2 can be picked now
    assigned_partner = food_delivery_core.assign_delivery_partner(
            order_id=order2.order_id
        )
    print(assigned_partner.log())

    # Validate restuarant menu availability now
    assert restaurant.menu['Pizza'] == 1, "All Items Finished"

