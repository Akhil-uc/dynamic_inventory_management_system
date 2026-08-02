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
    start = time.perf_counter()
    fn(*args)
    return time.perf_counter() - start


def benchmark_update_cost(sizes):
    """For each dataset size, compare the cost of ONE quantity update:
    Phase 2 (rebuild the whole heap) vs. Phase 3 (touch one IPQ entry).
    """
    print(f"{'n (products)':>14} | {'Phase 2 rebuild (s)':>20} | "
          f"{'Phase 3 IPQ update (s)':>22} | {'Speedup':>10}")
    print("-" * 76)

    for n in sizes:
        products = {
            pid: Product(pid, f"Item {pid}", "Misc", random.randint(1, 500), 9.99)
            for pid in range(n)
        }

        rebuild_time = time_it(naive_rebuild_heap, products)

        ipq = IndexedPriorityQueue()
        for product in products.values():
            ipq.push_or_update(product.product_id, product.quantity)

        ipq_time = time_it(ipq.push_or_update, 0, 42)

        speedup = rebuild_time / ipq_time if ipq_time > 0 else float("inf")
        print(f"{n:>14,} | {rebuild_time:>20.6f} | {ipq_time:>22.6f} | "
              f"{speedup:>9.1f}x")


def benchmark_end_to_end_operations(n):
    """Time realistic end-to-end InventoryManager operations against a
    dataset of n products, using the Phase 3 implementation.

    Console output from InventoryManager's own print() calls is
    suppressed with redirect_stdout so the timing table stays
    readable; only the numbers below are printed.
    """
    inventory = InventoryManager()
    sink = io.StringIO()

    with contextlib.redirect_stdout(sink):
        start = time.perf_counter()
        for pid in range(n):
            inventory.add_product(
                Product(pid, f"Item {pid}", "Misc", random.randint(1, 500), 9.99)
            )
        add_time = time.perf_counter() - start

        sample_ids = random.sample(range(n), min(1000, n))

        start = time.perf_counter()
        for pid in sample_ids:
            inventory.search_product(pid)
        search_time = time.perf_counter() - start

        start = time.perf_counter()
        for pid in sample_ids:
            inventory.update_product(pid, quantity=random.randint(1, 500))
        update_time = time.perf_counter() - start

        start = time.perf_counter()
        inventory.display_low_stock(threshold=10)
        low_stock_time = time.perf_counter() - start

    print(f"\nEnd-to-end timings for n = {n:,} products "
          f"(1,000-operation samples where applicable):")
    print(f"  add_product x{n:<8,}: {add_time:.4f}s total")
    print(f"  search_product x1,000: {search_time:.4f}s total")
    print(f"  update_product x1,000: {update_time:.4f}s total")
    print(f"  display_low_stock:     {low_stock_time:.4f}s")


if __name__ == "__main__":
    random.seed(42)

    print("=" * 76)
    print("Single-update cost: Phase 2 rebuild vs. Phase 3 IPQ")
    print("=" * 76)
    benchmark_update_cost([100, 1_000, 5_000, 10_000, 20_000])

    print("\n" + "=" * 76)
    print("End-to-end InventoryManager operation timings (Phase 3)")
    print("=" * 76)
    for size in (1_000, 10_000, 20_000):
        benchmark_end_to_end_operations(size)
