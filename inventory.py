import threading
from collections import deque

from ipq import IndexedPriorityQueue


class InventoryManager:

    def __init__(self):

        # Hash Table
        self.products = {}

        # Queue
        self.orders = deque()

        # Indexed Priority Queue (min-heap + lazy deletion, Phase 3)
        self.low_stock_queue = IndexedPriorityQueue()

        # Guards every mutating operation below so that concurrent
        # requests from multiple users cannot interleave and corrupt
        # the hash table, order queue, or priority queue. Re-entrant
        # so a locking method can safely call another locking method.
        self._lock = threading.RLock()

    
    # Product Functions (Hash Table)
    

    def add_product(self, product):
        """Insert a product into the hash table. O(1) average case.

        Returns:
            bool: True if added, False if a product with that ID
                  already exists.
        """
        with self._lock:
            if product.product_id in self.products:
                print("Product already exists.\n")
                return False

            self.products[product.product_id] = product
            self.low_stock_queue.push_or_update(
                product.product_id, product.quantity
            )

            print("Product added successfully.\n")
            return True

    def search_product(self, product_id):
        """Look up a product by ID. O(1) average case.

        Returns:
            Product | None
        """
        with self._lock:
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
        with self._lock:
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
                # O(log n) amortized -- Phase 2 rebuilt the entire
                # heap here; Phase 3 only touches this one entry.
                self.low_stock_queue.push_or_update(product_id, quantity)

            if price is not None:
                product.price = price

            print("Product updated successfully.\n")
            return True

    def delete_product(self, product_id):
        """Remove a product from the hash table. O(1) average case.

        Returns:
            bool: True if deleted, False if the product did not exist.
        """
        with self._lock:
            if product_id not in self.products:
                print("Product not found.\n")
                return False

            del self.products[product_id]
            self.low_stock_queue.remove(product_id)

            print("Product deleted successfully.\n")
            return True

    def display_inventory(self):
        """Print every product currently in the hash table.

        Returns:
            list[Product]: the products displayed.
        """
        with self._lock:
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
        with self._lock:
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
        with self._lock:
            if not self.orders:
                print("No pending orders.\n")
                return {"status": "empty"}

            product_id, quantity = self.orders.popleft()

            product = self.products[product_id]

            if product.quantity >= quantity:

                product.quantity -= quantity
                self.low_stock_queue.push_or_update(
                    product_id, product.quantity
                )

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

            return result

    
    # Low-Stock Monitoring (Indexed Priority Queue)
    

    def display_low_stock(self, threshold=10):
        """Print (and return) every product at or below `threshold`.

        Returns:
            list[Product]: low-stock products, ascending by quantity.
        """
        with self._lock:
            print("\n LOW STOCK PRODUCTS \n")

            matches = self.low_stock_queue.items_at_or_below(threshold)
            low_stock_products = [self.products[pid] for _, pid in matches]

            for product in low_stock_products:
                print(product)

            if not low_stock_products:
                print("No low stock products.\n")

            return low_stock_products
