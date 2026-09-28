class Product:

    def __init__(self, id: str, name: str, price: int):
        self.id = id
        self.name = name
        self.price = price


class Slot:

    def __init__(self, product_id: str, remaining_unit: int):
        self.product_id = product_id
        self.remaining_unit = remaining_unit


