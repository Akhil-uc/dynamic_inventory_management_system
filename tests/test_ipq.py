import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ipq import IndexedPriorityQueue


class TestIndexedPriorityQueue(unittest.TestCase):

    def setUp(self):
        self.ipq = IndexedPriorityQueue()

    def test_push_and_peek_min(self):
        self.ipq.push_or_update("A", 5)
        self.ipq.push_or_update("B", 2)
        self.ipq.push_or_update("C", 9)
        self.assertEqual(self.ipq.peek_min(), (2, "B"))

    def test_len_tracks_live_entries_only(self):
        self.ipq.push_or_update("A", 5)
        self.ipq.push_or_update("B", 2)
        self.assertEqual(len(self.ipq), 2)
        self.ipq.remove("A")
        self.assertEqual(len(self.ipq), 1)

    def test_update_replaces_old_priority(self):
        self.ipq.push_or_update("A", 5)
        self.ipq.push_or_update("A", 1)
        self.assertEqual(self.ipq.peek_min(), (1, "A"))
        self.assertEqual(len(self.ipq), 1)

    def test_update_does_not_resurface_stale_priority(self):
        self.ipq.push_or_update("A", 1)
        self.ipq.push_or_update("B", 5)
        self.ipq.push_or_update("A", 100)
        self.assertEqual(self.ipq.peek_min(), (5, "B"))

    def test_remove_missing_item_returns_false(self):
        self.assertFalse(self.ipq.remove("ghost"))

    def test_peek_min_on_empty_queue(self):
        self.assertIsNone(self.ipq.peek_min())

    def test_peek_min_after_removing_everything(self):
        self.ipq.push_or_update("A", 1)
        self.ipq.remove("A")
        self.assertIsNone(self.ipq.peek_min())

    def test_items_at_or_below_threshold_ascending(self):
        self.ipq.push_or_update("A", 8)
        self.ipq.push_or_update("B", 2)
        self.ipq.push_or_update("C", 15)
        self.ipq.push_or_update("D", 5)
        result = self.ipq.items_at_or_below(10)
        self.assertEqual(result, [(2, "B"), (5, "D"), (8, "A")])

    def test_items_at_or_below_excludes_stale_entries(self):
        self.ipq.push_or_update("A", 2)
        self.ipq.push_or_update("A", 999)  # A restocked, no longer low
        result = self.ipq.items_at_or_below(10)
        self.assertEqual(result, [])

    def test_compaction_preserves_correctness(self):
        for round_num in range(100):
            for item_id in range(5):
                self.ipq.push_or_update(item_id, round_num * 10 + item_id)

        self.assertEqual(len(self.ipq), 5)
        min_priority, min_id = self.ipq.peek_min()
        self.assertEqual(min_id, 0)
        self.assertEqual(min_priority, 99 * 10 + 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
