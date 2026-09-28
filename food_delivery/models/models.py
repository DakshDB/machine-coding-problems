
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PLACED = 'placed'
    ACCEPTED = 'accepted'
    PICKED_UP = 'picked_up'
    DELIVERED = 'delivered'

class User:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
    
    def log(self):
        return f"\nUser ID : {self.user_id} | Name : {self.name}"


class Restaurant:
    def __init__(self, restaurant_id: str, name: str, menu: dict):
        self.restaurant_id = restaurant_id
        self.name = name 
        self.menu = menu

    def log(self):
        return f"\nRestaurant ID : {self.restaurant_id} | Name : {self.name} | Available Items : {self.menu}" 


class DeliveryPartner:
    def __init__(self, partner_id: str, name: str):
        self.partner_id = partner_id
        self.name = name

    def log(self):
        return f"\nPartner ID : {self.partner_id} | Name : {self.name}"


class Order:
    def __init__(self, order_id: str, status: OrderStatus, last_status_time: datetime, delivery_partner_id=None):
        self.order_id = order_id
        self.status= status
        self.last_status_time = last_status_time
        self.delivery_partner_id = delivery_partner_id
    
    def log(self):
        return f"\nOrder ID : {self.order_id} | Status : {self.status.name} | Update Time : {self.last_status_time} | Delivery Partner : {self.delivery_partner_id}"
