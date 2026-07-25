from collections import deque
import heapq


class InventoryManager:

    def __init__(self):

        # Hash Table
        self.products = {}

        # Queue
        self.orders = deque()

        # Min Heap
        self.low_stock_heap = []

    
    # Product Functions (Hash Table)
    

    def add_product(self, product):
        """Insert a product into the hash table. O(1) average case.

        Returns:
            bool: True if added, False if a product with that ID
                  already exists.
        """

        if product.product_id in self.products:
            print("Product already exists.\n")
            return False

        self.products[product.product_id] = product

        heapq.heappush(
            self.low_stock_heap,
            (product.quantity, product.product_id)
        )

        print("Product added successfully.\n")
        return True

    def search_product(self, product_id):
        """Look up a product by ID. O(1) average case.

        Returns:
            Product | None
        """

        product = self.products.get(product_id)

        if product:
            print(product)
        else:
            print("Product not found.")

        return product

    def update_product(self, product_id,
                       quantity=None,
                       price=None):
        """Update quantity and/or price for an existing product.

        Returns:
            bool: True if updated, False if the product does not exist
                  or the new quantity/price is invalid (negative).
        """

        if product_id not in self.products:
            print("Product not found.\n")
            return False

        if quantity is not None and quantity < 0:
            print("Quantity cannot be negative.\n")
            return False

        if price is not None and price < 0:
            print("Price cannot be negative.\n")
            return False

        product = self.products[product_id]

        if quantity is not None:
            product.quantity = quantity

        if price is not None:
            product.price = price

        self.rebuild_heap()

        print("Product updated successfully.\n")
        return True

    def delete_product(self, product_id):
        """Remove a product from the hash table. O(1) average case.

        Returns:
            bool: True if deleted, False if the product did not exist.
        """

        if product_id not in self.products:
            print("Product not found.\n")
            return False

        del self.products[product_id]

        self.rebuild_heap()

        print("Product deleted successfully.\n")
        return True

    def display_inventory(self):
        """Print every product currently in the hash table.

        Returns:
            list[Product]: the products displayed.
        """

        print("\n INVENTORY \n")

        if not self.products:
            print("Inventory is empty.\n")
            return []

        for product in self.products.values():
            print(product)

        print()
        return list(self.products.values())

    
    # Order Queue (FIFO)
    

    def place_order(self, product_id, quantity):
        """Enqueue a customer order. O(1).

        Returns:
            bool: True if the order was queued, False if the product
                  ID is invalid or quantity is not positive.
        """

        if product_id not in self.products:
            print("Invalid Product ID.\n")
            return False

        if quantity <= 0:
            print("Order quantity must be greater than zero.\n")
            return False

        self.orders.append((product_id, quantity))

        print("Order placed successfully.\n")
        return True

    def process_order(self):
        """Dequeue and fulfil the oldest pending order. O(1) dequeue.

        Returns:
            dict: {"status": "empty"} if there was nothing to process,
                  {"status": "success", "product_id", "quantity"} if
                  fulfilled, or
                  {"status": "insufficient_stock", "product_id",
                  "requested", "available"} if stock was too low.
        """

        if not self.orders:
            print("No pending orders.\n")
            return {"status": "empty"}

        product_id, quantity = self.orders.popleft()

        product = self.products[product_id]

        if product.quantity >= quantity:

            product.quantity -= quantity

            print(
                f"Processed Order:"
                f" {quantity} x {product.name}"
            )

            result = {
                "status": "success",
                "product_id": product_id,
                "quantity": quantity,
            }

        else:

            print(
                f"Insufficient stock for "
                f"{product.name}"
            )

            result = {
                "status": "insufficient_stock",
                "product_id": product_id,
                "requested": quantity,
                "available": product.quantity,
            }

        self.rebuild_heap()
        return result

    
    # Min-Heap Functions
    

    def rebuild_heap(self):
        """Rebuild the low-stock heap from scratch. O(n log n).

        Needed because heapq has no O(log n) "update key" operation,
        so any change to a product's quantity (update/delete/process
        order) invalidates the existing heap entries.
        """

        self.low_stock_heap = []

        for product in self.products.values():

            heapq.heappush(
                self.low_stock_heap,
                (product.quantity,
                 product.product_id)
            )

    def display_low_stock(self, threshold=10):
        """Print (and return) every product at or below `threshold`.

        Returns:
            list[Product]: low-stock products, ascending by quantity.
        """

        print("\n LOW STOCK PRODUCTS \n")

        temp_heap = self.low_stock_heap.copy()

        low_stock_products = []

        while temp_heap:

            quantity, pid = heapq.heappop(temp_heap)

            if quantity <= threshold:
                low_stock_products.append(self.products[pid])
                print(self.products[pid])

        if not low_stock_products:
            print("No low stock products.\n")

        return low_stock_products
