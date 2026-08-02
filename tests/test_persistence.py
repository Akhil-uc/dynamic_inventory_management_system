import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import persistence
from inventory import InventoryManager
from product import Product


class TestPersistence(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.remove(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_load_on_missing_database_returns_false(self):
        inventory = InventoryManager()
        self.assertFalse(persistence.load_inventory(inventory, self.db_path))

    def test_save_then_load_restores_products(self):
        inventory = InventoryManager()
        inventory.add_product(Product(1, "Keyboard", "Electronics", 12, 45.00))
        inventory.add_product(Product(2, "Monitor", "Electronics", 4, 199.99))

        self.assertTrue(persistence.save_inventory(inventory, self.db_path))

        restored = InventoryManager()
        self.assertTrue(persistence.load_inventory(restored, self.db_path))

        self.assertEqual(len(restored.products), 2)
        self.assertEqual(restored.products[1].name, "Keyboard")
        self.assertEqual(restored.products[2].quantity, 4)

    def test_save_then_load_restores_pending_orders_in_order(self):
        inventory = InventoryManager()
        inventory.add_product(Product(1, "Keyboard", "Electronics", 12, 45.00))
        inventory.place_order(1, 2)
        inventory.place_order(1, 3)

        persistence.save_inventory(inventory, self.db_path)

        restored = InventoryManager()
        persistence.load_inventory(restored, self.db_path)

        self.assertEqual(list(restored.orders), [(1, 2), (1, 3)])

    def test_low_stock_queue_is_rebuilt_after_load(self):
        inventory = InventoryManager()
        inventory.add_product(Product(1, "Cable", "Accessories", 2, 5.00))
        persistence.save_inventory(inventory, self.db_path)

        restored = InventoryManager()
        persistence.load_inventory(restored, self.db_path)

        low_stock = restored.display_low_stock(threshold=10)
        self.assertEqual([p.product_id for p in low_stock], [1])

    def test_save_overwrites_previous_snapshot(self):
        inventory = InventoryManager()
        inventory.add_product(Product(1, "Cable", "Accessories", 2, 5.00))
        persistence.save_inventory(inventory, self.db_path)

        inventory.delete_product(1)
        inventory.add_product(Product(2, "Charger", "Accessories", 9, 15.00))
        persistence.save_inventory(inventory, self.db_path)

        restored = InventoryManager()
        persistence.load_inventory(restored, self.db_path)

        self.assertNotIn(1, restored.products)
        self.assertIn(2, restored.products)


if __name__ == "__main__":
    unittest.main(verbosity=2)
