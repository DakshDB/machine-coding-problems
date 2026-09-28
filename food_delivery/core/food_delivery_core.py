from models.models import DeliveryPartner
from datetime import datetime
from os import curdir
from models.errors import OrderStatusCantBeUpdated
from models.models import OrderStatus
from models.models import Order
from models.errors import InsufficientInventory
from uuid import uuid4
import threading

from models.models import *
from models.errors import *

class FoodDeliveryCore:

    def __init__(self):
        
        self.users: dict[str, User] = {}
        self.orders: dict[str, Order] = {}
        self.restaurants: dict[str, Restaurant] = {}
        self.delivery_partners: dict[str, DeliveryPartner] = {}
        self.available_delivery_partners: set[DeliveryPartner] = set()

        self.lock = threading.RLock()

    def add_restaurant(self, name: str, menu: dict) -> Restaurant:
        with self.lock:
            restaurant_id = str(uuid4())
            restaurant = Restaurant(
                restaurant_id=restaurant_id,
                name=name,
                menu=menu
            )
            self.restaurants[restaurant_id] = restaurant
            return restaurant

    def add_delivery_partner(self, name: str) -> DeliveryPartner:
        with self.lock:
            delivery_partner_id = str(uuid4())
            delivery_partner = DeliveryPartner(
                partner_id=delivery_partner_id,
                name=name
            )
            self.available_delivery_partners.add(delivery_partner)
            self.delivery_partners[delivery_partner.partner_id] = delivery_partner
            return delivery_partner

    def add_user(self, name: str) -> User:
        with self.lock:
            user_id = str(uuid4())
            user = User(
                user_id=user_id,
                name=name
            )
            self.users[user_id] = user
            return user

    def place_order(self, user_id: str, restaurant_id: str, items: dict) -> Order:
         with self.lock:

            user = self.users.get(user_id, None)
            if user is None:
                raise UserNotFound()

            restaurant = self.restaurants.get(restaurant_id, None)
            if restaurant is None:
                raise RestaurantNotFound()

            restaurant_items = restaurant.menu

            # Check Availability
            for item, qty in items.items():
                if restaurant_items.get(item, 0) < qty:
                    raise InsufficientInventory()

            # Accept the items 
            for item, qty in items.items():
                restaurant_items[item] -= qty

            # Place Order
            order = Order(
                order_id=str(uuid4()),
                status=OrderStatus.PLACED,
                last_status_time=datetime.now()
            )
            self.orders[order.order_id] = order

            return order


    def assign_delivery_partner(self, order_id: str) -> DeliveryPartner:
        with self.lock:

            order = self.orders.get(order_id, None)
            if order is None:
                raise OrderNotFound()

            if order.status != OrderStatus.PLACED:
                raise OrderNotInStatusToBePicked()

            if len(self.available_delivery_partners) == 0:
                raise NoDeliveryPartnerAvailable()

            delivery_partner = self.available_delivery_partners.pop()

            order.delivery_partner_id = delivery_partner.partner_id

            # Mark as Accepted
            order.status = OrderStatus.ACCEPTED
            order.last_status_time=datetime.now()

            return delivery_partner

    def update_order_status(self, order_id: str, status: OrderStatus, current_time = None) -> Order:
        with self.lock:

            order = self.orders.get(order_id, None)
            if order is None:
                raise OrderNotFound()
            
            if order.status == OrderStatus.PLACED:
                raise OrderStatusCantBeUpdated()

            if order.status == status:
                return

            if order.status == OrderStatus.DELIVERED and status == OrderStatus.PICKED_UP:
                raise OrderStatusCantBeUpdated()

            order.status = status
            current_time = current_time or datetime.now()
            order.last_status_time=current_time

            if order.status == OrderStatus.DELIVERED:
                delivery_partner = self.delivery_partners[order.delivery_partner_id]
                self.available_delivery_partners.add(delivery_partner)
                

            return order



