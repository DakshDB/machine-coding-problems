

from models.errors import InvalidState
from models.models import Slot
from models.models import Product
from collections import defaultdict
from models.constants import Denomination
from models.constants import MachineState


class VendingMachine:

    def __init__(self, products: list[Product], slots: list[Slot], existing_coins:list[Denomination]):
        self.coin_inventory: dict[Denomination, int] = defaultdict(int)
        self.balance: dict[Denomination, int] = defaultdict(int)

        self.products: dict[set, Product] = {}
        for product in products:
            self.products[product.id] = product

        self.slots: dict[str, int] = {}
        for slot in slots:
            self.slots[slot.product_id] = slot.remaining_unit

        for existing_coin in existing_coins:
            self.coin_inventory[existing_coin] +=1   

        self.machine_state = MachineState.IDLE 

    def _get_current_balance(self):
        balance = 0
        for coin, count in self.balance.items():
            balance += coin.value * count 
        return balance

    def insert_money(self, coins: list[Denomination]):
        if self.machine_state not in [MachineState.IDLE, MachineState.COLLECTING_MONEY]:
            raise InvalidState()
        
        self.machine_state = MachineState.COLLECTING_MONEY

        for coin in coins:
            self.balance[coin] += 1
        
        return self._get_current_balance()


    def _get_return_coins(self, return_amount):
        if return_amount == 0:
            return True, []

        coins_to_return = []
        for val, coin in reversed(Denomination.__members__.items()):
            count = self.coin_inventory[coin]
            if return_amount >= coin.value:
                for i in range(0, count):
                    if return_amount >= coin.value:
                        return_amount -= coin.value
                        coins_to_return.append(coin)

        
        if return_amount == 0:
            for coin in coins_to_return:
                self.coin_inventory[coin] -= 1
            return True, coins_to_return
        else:
            return False, []
    
    def _move_balance_to_coin_inventory(self):
        for coin, count in self.balance.items():
            self.coin_inventory[coin] += count
        
        self.balance = defaultdict(int)


    def select_product(self, code: str):
        if self.machine_state != MachineState.COLLECTING_MONEY:
            raise InvalidState()
        self.machine_state = MachineState.DISPENSING
        # Check if prouct is available
        available_units = self.slots[code]
        if available_units <= 0 :
            return False, self.cancel(), "Not Available"

        product = self.products[code]
        
        balance = self._get_current_balance()
        if balance < product.price:
            return False, self.cancel(), "Balance Low"
        
        return_amount  = balance - product.price

        is_return_possible, coins = self._get_return_coins(return_amount)
        if is_return_possible == False:
            return False, self.cancel(), "Refund Not Possible"

        # Reduce the remaining count
        self.slots[product.id] -=1

        self._move_balance_to_coin_inventory()

        self.machine_state = MachineState.IDLE
        return True, return_amount, "Dispatched"

    def cancel(self):
        balance = self._get_current_balance()
        self.balance = defaultdict(int)
        self.machine_state = MachineState.IDLE
        return balance

    def get_available_products(self):
        products = []
        for product_id, product in self.products.items():
            remaining_units = self.slots[product_id]
            if remaining_units > 0:
                products.append(
                    {
                        "id": product_id,
                        "name": product.name,
                        "price": product.price,
                        "remaining_units": remaining_units
                    }
                )

        return products
        




