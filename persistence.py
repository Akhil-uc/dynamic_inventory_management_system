import sqlite3
from collections import deque

from ipq import IndexedPriorityQueue
from product import Product

DEFAULT_DB_PATH = "inventory.db"


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            position INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL
        )
        """
    )
    return conn


def save_inventory(inventory_manager, db_path=DEFAULT_DB_PATH):
    """Persist the current products and pending orders to SQLite.

    Overwrites whatever was previously saved at `db_path`.

    Returns:
        bool: True on success.
    """
    conn = _connect(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM products")
            conn.execute("DELETE FROM orders")

            conn.executemany(
                "INSERT INTO products "
                "(product_id, name, category, quantity, price) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (p.product_id, p.name, p.category, p.quantity, p.price)
                    for p in inventory_manager.products.values()
                ],
            )

            conn.executemany(
                "INSERT INTO orders (product_id, quantity) VALUES (?, ?)",
                list(inventory_manager.orders),
            )
        return True
    finally:
        conn.close()


def load_inventory(inventory_manager, db_path=DEFAULT_DB_PATH):
    """Load products and pending orders from SQLite into an existing
    InventoryManager, replacing its hash table, order queue, and
    low-stock priority queue with what is stored on disk.

    Returns:
        bool: True if a database with saved products was found and
              loaded, False if there was nothing to load (e.g. first
              run, no file yet).
    """
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT product_id, name, category, quantity, price "
            "FROM products"
        ).fetchall()

        if not rows:
            return False

        inventory_manager.products = {}
        inventory_manager.low_stock_queue = IndexedPriorityQueue()

        for pid, name, category, quantity, price in rows:
            product = Product(pid, name, category, quantity, price)
            inventory_manager.products[pid] = product
            inventory_manager.low_stock_queue.push_or_update(pid, quantity)

        order_rows = conn.execute(
            "SELECT product_id, quantity FROM orders ORDER BY position"
        ).fetchall()
        inventory_manager.orders = deque(order_rows)

        return True
    finally:
        conn.close()
