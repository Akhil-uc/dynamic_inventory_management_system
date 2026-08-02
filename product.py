class Product:
    """
    Represents a single product in inventory.

    Raises:
        ValueError: if quantity or price is negative.
    """

    def __init__(self, product_id, name, category, quantity, price):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if price < 0:
            raise ValueError("Price cannot be negative.")

        self.product_id = product_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = price

    def __str__(self):
        return (
            f"ID: {self.product_id} | "
            f"Name: {self.name} | "
            f"Category: {self.category} | "
            f"Quantity: {self.quantity} | "
            f"Price: ${self.price:.2f}"
        )
