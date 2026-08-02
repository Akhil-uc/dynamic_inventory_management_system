import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from inventory import InventoryManager
from product import Product


class TestConcurrentAccess(unittest.TestCase):
    def test_concurrent_orders_no_lost_updates(self):
        inventory = InventoryManager()
        inventory.add_product(
            Product(1, "Widget", "Misc", 10_000, 1.00)
        )

        num_threads = 20
        orders_per_thread = 50

        def place_many_orders():
            for _ in range(orders_per_thread):
                inventory.place_order(1, 1)

        threads = [
            threading.Thread(target=place_many_orders)
            for _ in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(inventory.orders), num_threads * orders_per_thread)

    def test_concurrent_order_processing_conserves_stock(self):
        inventory = InventoryManager()
        starting_stock = 5_000
        inventory.add_product(
            Product(1, "Widget", "Misc", starting_stock, 1.00)
        )

        for _ in range(starting_stock):
            inventory.place_order(1, 1)

        def process_all():
            while inventory.process_order()["status"] != "empty":
                pass

        threads = [threading.Thread(target=process_all) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(inventory.products[1].quantity, 0)
        self.assertEqual(len(inventory.orders), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
