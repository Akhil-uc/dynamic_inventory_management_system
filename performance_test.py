import contextlib
import heapq
import io
import random
import time

from inventory import InventoryManager
from ipq import IndexedPriorityQueue
from product import Product


def naive_rebuild_heap(products):
    """Reproduces the Phase 2 approach: throw everything away and
    rebuild the whole heap from scratch. O(n log n) every call.
    """
    heap = []
    for product in products.values():
        heapq.heappush(heap, (product.quantity, product.product_id))
    return heap


def time_it(fn, *args):
    """Measure execution time of a single function call."""
    start = time.perf_counter()
    fn(*args)
    return time.perf_counter() - start


def benchmark_update_cost(sizes):
    """Compare the cost of a single quantity update:

    Phase 2:
        Rebuild the entire heap after an update (O(n log n))

    Phase 3:
        Update a single Indexed Priority Queue entry (O(log n))

    Speedup is computed from full-precision timings. Displayed timings
    are rounded for readability.
    """

    print(f"{'n (products)':>14} | {'Phase 2 rebuild (s)':>20} | "
          f"{'Phase 3 IPQ update (s)':>22} | {'Speedup':>10}")
    print("-" * 80)

    NUM_UPDATES = 10000

    for n in sizes:
        # Generate test dataset
        products = {
            pid: Product(
                pid,
                f"Item {pid}",
                "Misc",
                random.randint(1, 500),
                9.99,
            )
            for pid in range(n)
        }

        # -------------------------------
        # Phase 2: rebuild whole heap
        # -------------------------------
        rebuild_time = time_it(naive_rebuild_heap, products)

        # -------------------------------
        # Phase 3: Indexed Priority Queue
        # -------------------------------
        ipq = IndexedPriorityQueue()

        for product in products.values():
            ipq.push_or_update(product.product_id, product.quantity)

        # Average over many updates for a stable measurement
        start = time.perf_counter()

        for _ in range(NUM_UPDATES):
            ipq.push_or_update(
                0,
                random.randint(1, 500)
            )

        ipq_time = (time.perf_counter() - start) / NUM_UPDATES

        speedup = rebuild_time / ipq_time

        print(
            f"{n:>14,} | "
            f"{rebuild_time:>20.8f} | "
            f"{ipq_time:>22.8f} | "
            f"{speedup:>9.1f}x"
        )

    print("\nNote: Speedup values were computed using full-precision timing "
          "measurements. The displayed execution times are rounded for "
          "readability, so dividing the printed values may not exactly "
          "reproduce the reported speedups.")


def benchmark_end_to_end_operations(n):
    """Time realistic InventoryManager operations using the Phase 3
    implementation.

    Output from InventoryManager is suppressed so that only timing
    information is displayed.
    """

    inventory = InventoryManager()
    sink = io.StringIO()

    with contextlib.redirect_stdout(sink):

        # -------------------------------
        # Add products
        # -------------------------------
        start = time.perf_counter()

        for pid in range(n):
            inventory.add_product(
                Product(
                    pid,
                    f"Item {pid}",
                    "Misc",
                    random.randint(1, 500),
                    9.99,
                )
            )

        add_time = time.perf_counter() - start

        sample_ids = random.sample(range(n), min(1000, n))

        # -------------------------------
        # Search
        # -------------------------------
        start = time.perf_counter()

        for pid in sample_ids:
            inventory.search_product(pid)

        search_time = time.perf_counter() - start

        # -------------------------------
        # Update
        # -------------------------------
        start = time.perf_counter()

        for pid in sample_ids:
            inventory.update_product(
                pid,
                quantity=random.randint(1, 500),
            )

        update_time = time.perf_counter() - start

        # -------------------------------
        # Low-stock query
        # -------------------------------
        start = time.perf_counter()

        inventory.display_low_stock(threshold=10)

        low_stock_time = time.perf_counter() - start

    print(
        f"\nEnd-to-end timings for n = {n:,} products "
        f"(1,000-operation samples where applicable):"
    )

    print(f"  add_product x{n:<8,}: {add_time:.4f}s total")
    print(f"  search_product x1,000: {search_time:.4f}s total")
    print(f"  update_product x1,000: {update_time:.4f}s total")
    print(f"  display_low_stock:     {low_stock_time:.4f}s")


if __name__ == "__main__":

    random.seed(42)

    print("=" * 80)
    print("Single-update cost: Phase 2 rebuild vs. Phase 3 IPQ")
    print("=" * 80)

    benchmark_update_cost(
        [100, 1_000, 5_000, 10_000, 20_000]
    )

    print("\n" + "=" * 80)
    print("End-to-end InventoryManager operation timings (Phase 3)")
    print("=" * 80)

    for size in (1_000, 10_000, 20_000):
        benchmark_end_to_end_operations(size)
