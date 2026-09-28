# Food Delivery System 


Entities

- User
    - user_id

- Restaurant 
    - restaurant_id
    - food_stock

- Delivery Partner
    - partner_id

- Order
    - order_id
    - status (PLACED|ACCEPTED|PICKED_UP|DELIVERED)


# Operations 

- add_restaurant(name: str, menu: dict) -> Restaurant 

- add_delivery_partner(name: str) -> Delivery partner 

- add_user(name: str) -> User

- place_order(user_id: str, restaurant_id: str, items: dict) -> Order|Error

- assign_delivery_partner(order_id) -> partner_id

- update_order_status(order_id: str, status: Status, current_time) - Order



Constraints 

- String Concurrency  - Threading Lock
- State Machine - Proper Validation
- No O(N) polling - Using Sets and proper Datastyrcuture 
- Time passed as variable to have time testability