

from models.models import Slot
from models.models import Product
from models.constants import Denomination
from core.vending_machine import VendingMachine


def _populate_coin_inventory():
    existing_coins = []
    for denomination, d in Denomination.__members__.items():
        for i in range(0, 10):
            existing_coins.append(d)
    return existing_coins

if __name__ == '__main__':
    
    print("Vending Machine")

    existing_coins = _populate_coin_inventory()

    product1 = Product("A1", "Coke", 10)
    product2 = Product("B2", "Pepsi", 40)
    product3 = Product("D1", "Fanta", 52)

    slot1 = Slot(product1.id, 2)
    slot2 = Slot(product2.id, 2)
    slot3 = Slot(product3.id, 2)

    vending_machine = VendingMachine(products=[product1, product2, product3], slots=[slot1,slot2,slot3], existing_coins=existing_coins)

    available_products = vending_machine.get_available_products()
    print(available_products)

    balance =  vending_machine.insert_money(
        [
            Denomination.HUNDRED,
            
        ]
    )
    print(f"Balance = {balance}")

    # refund = vending_machine.cancel()
    # print(f"Refund = {refund}")

    is_dispatched, amount, message = vending_machine.select_product(product1.id)
    print(f"Dispatched = {is_dispatched} \nAmount = {amount} \nMessage = {message}\n")

    balance =  vending_machine.insert_money(
        [
            Denomination.HUNDRED,
            
        ]
    )

    is_dispatched, amount, message = vending_machine.select_product(product1.id)
    print(f"Dispatched = {is_dispatched} \nAmount = {amount} \nMessage = {message}\n")
    
    balance =  vending_machine.insert_money(
        [
            Denomination.HUNDRED,
            
        ]
    )
    
    is_dispatched, amount, message = vending_machine.select_product(product1.id)
    print(f"Dispatched = {is_dispatched} \nAmount = {amount} \nMessage = {message}\n")

    available_products = vending_machine.get_available_products()
    print(available_products)