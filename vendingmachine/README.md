# Vending Machine 

- Product 
    - id 
    - name
    - price

- Slot 
    - product_id
    - remaining_unit

- CoinInventory
    - coins 

Operations 

- insert_money(coins) - balance
- select_product(code)
- cancel()
- get_available_products()

Machine States
IDLE - COLLECTING_MONEY - DISPENSING - IDLE 