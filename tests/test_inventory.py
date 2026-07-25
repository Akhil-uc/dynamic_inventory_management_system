import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from inventory import InventoryManager
from product import Product


class TestHashTableOperations(unittest.TestCase):
    """Add / search / update / delete on the product hash table."""

    def setUp(self):
        self.inventory = InventoryManager()
        self.product = Product(101, "Wireless Mouse", "Electronics", 50, 19.99)

    def test_add_product_success(self):
        self.assertTrue(self.inventory.add_product(self.product))
        self.assertIn(101, self.inventory.products)

    def test_add_duplicate_product_is_rejected(self):
        self.inventory.add_product(self.product)
        duplicate = Product(101, "Wireless Mouse v2", "Electronics", 10, 25.00)
        self.assertFalse(self.inventory.add_product(duplicate))
        # original product must be unchanged
        self.assertEqual(self.inventory.products[101].name, "Wireless Mouse")

    def test_search_existing_product(self):
        self.inventory.add_product(self.product)
        found = self.inventory.search_product(101)
        self.assertIsNotNone(found)
        self.assertEqual(found.product_id, 101)

    def test_search_nonexistent_product_returns_none(self):
        self.assertIsNone(self.inventory.search_product(999))

    def test_update_existing_product(self):
        self.inventory.add_product(self.product)
        updated = self.inventory.update_product(101, quantity=5, price=15.50)
        self.assertTrue(updated)
        self.assertEqual(self.inventory.products[101].quantity, 5)
        self.assertEqual(self.inventory.products[101].price, 15.50)

    def test_update_nonexistent_product_fails(self):
        self.assertFalse(self.inventory.update_product(999, quantity=5))

    def test_update_with_negative_quantity_is_rejected(self):
        self.inventory.add_product(self.product)
        self.assertFalse(self.inventory.update_product(101, quantity=-5))
        # unchanged
        self.assertEqual(self.inventory.products[101].quantity, 50)

    def test_delete_existing_product(self):
        self.inventory.add_product(self.product)
        self.assertTrue(self.inventory.delete_product(101))
        self.assertNotIn(101, self.inventory.products)

    def test_delete_nonexistent_product_fails(self):
        self.assertFalse(self.inventory.delete_product(999))

    def test_display_inventory_empty(self):
        self.assertEqual(self.inventory.display_inventory(), [])

    def test_display_inventory_nonempty(self):
        self.inventory.add_product(self.product)
        products = self.inventory.display_inventory()
        self.assertEqual(len(products), 1)


class TestProductValidation(unittest.TestCase):
    """Edge cases enforced at construction time."""

    def test_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            Product(1, "Bad Item", "Misc", -1, 10.0)

    def test_negative_price_raises(self):
        with self.assertRaises(ValueError):
            Product(1, "Bad Item", "Misc", 10, -5.0)


class TestOrderQueue(unittest.TestCase):
    """FIFO queue used for customer orders."""

    def setUp(self):
        self.inventory = InventoryManager()
        self.inventory.add_product(
            Product(201, "USB-C Cable", "Accessories", 20, 8.99)
        )
        self.inventory.add_product(
            Product(202, "Laptop Stand", "Accessories", 3, 34.99)
        )

    def test_place_order_valid(self):
        self.assertTrue(self.inventory.place_order(201, 5))
        self.assertEqual(len(self.inventory.orders), 1)

    def test_place_order_invalid_product(self):
        self.assertFalse(self.inventory.place_order(999, 1))
        self.assertEqual(len(self.inventory.orders), 0)

    def test_place_order_zero_or_negative_quantity(self):
        self.assertFalse(self.inventory.place_order(201, 0))
        self.assertFalse(self.inventory.place_order(201, -3))

    def test_process_order_empty_queue(self):
        result = self.inventory.process_order()
        self.assertEqual(result["status"], "empty")

    def test_process_order_sufficient_stock_fifo(self):
        self.inventory.place_order(201, 5)
        self.inventory.place_order(202, 1)

        first = self.inventory.process_order()
        self.assertEqual(first["status"], "success")
        self.assertEqual(first["product_id"], 201)  # FIFO: first in, first out
        self.assertEqual(self.inventory.products[201].quantity, 15)

        second = self.inventory.process_order()
        self.assertEqual(second["product_id"], 202)

    def test_process_order_insufficient_stock(self):
        self.inventory.place_order(202, 10)  # only 3 in stock
        result = self.inventory.process_order()
        self.assertEqual(result["status"], "insufficient_stock")
        self.assertEqual(result["available"], 3)
        # stock must be unchanged after a failed fulfilment
        self.assertEqual(self.inventory.products[202].quantity, 3)


class TestLowStockMinHeap(unittest.TestCase):
    """Min-heap used to surface products that need restocking."""

    def setUp(self):
        self.inventory = InventoryManager()
        self.inventory.add_product(Product(301, "Notebook", "Office", 2, 2.50))
        self.inventory.add_product(Product(302, "Stapler", "Office", 40, 6.00))
        self.inventory.add_product(Product(303, "Pen Pack", "Office", 8, 3.25))

    def test_low_stock_detection_below_threshold(self):
        low_stock = self.inventory.display_low_stock(threshold=10)
        ids = {p.product_id for p in low_stock}
        self.assertEqual(ids, {301, 303})
        self.assertNotIn(302, ids)

    def test_low_stock_empty_when_all_above_threshold(self):
        low_stock = self.inventory.display_low_stock(threshold=1)
        self.assertEqual(low_stock, [])

    def test_heap_reflects_updates_after_rebuild(self):
        # Notebook restocked above threshold, Stapler drops below it
        self.inventory.update_product(301, quantity=100)
        self.inventory.update_product(302, quantity=1)

        low_stock = self.inventory.display_low_stock(threshold=10)
        ids = {p.product_id for p in low_stock}
        self.assertEqual(ids, {302, 303})

    def test_heap_reflects_deletion(self):
        self.inventory.delete_product(301)
        low_stock = self.inventory.display_low_stock(threshold=10)
        ids = {p.product_id for p in low_stock}
        self.assertEqual(ids, {303})


if __name__ == "__main__":
    unittest.main(verbosity=2)
