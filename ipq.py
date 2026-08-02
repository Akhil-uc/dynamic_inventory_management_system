import heapq

_LIVE = "live"
_REMOVED = "removed"


class IndexedPriorityQueue:
    """Min-priority queue keyed by (priority, item_id).

    Supports O(log n) push and O(log n) amortized update/remove,
    versus the O(n log n) full rebuild it replaces.
    """

    def __init__(self):
        self._heap = []          # list of [priority, item_id, status]
        self._entry_finder = {}  # item_id -> its current live entry
        self._live_count = 0
        self._stale_count = 0

    def __len__(self):
        return self._live_count

    def push_or_update(self, item_id, priority):
        """Insert a new item, or update an existing item's priority.

        O(log n) amortized. The previous entry for `item_id`, if any,
        is marked stale in O(1); a fresh entry is then pushed onto the
        heap in O(log n).
        """
        if item_id in self._entry_finder:
            self._mark_removed(item_id)

        entry = [priority, item_id, _LIVE]
        self._entry_finder[item_id] = entry
        heapq.heappush(self._heap, entry)
        self._live_count += 1

        # Reclaim space once stale entries dominate the heap so it
        # cannot grow without bound across many updates. This is the
        # one O(n log n) step in the structure, but because it only
        # runs once roughly half the heap is stale, its cost is
        # amortized to O(log n) per update over the sequence of calls
        # that led up to it.
        if self._stale_count > self._live_count and self._stale_count > 32:
            self._compact()

    def remove(self, item_id):
        """Remove an item entirely. O(1) amortized (lazy deletion).

        Returns:
            bool: True if the item was present and removed.
        """
        return self._mark_removed(item_id)

    def peek_min(self):
        """Return (priority, item_id) for the smallest live entry
        without removing it, or None if the queue is empty.

        Amortized O(log n): stale entries sitting at the top of the
        heap are discarded lazily as part of this call.
        """
        while self._heap and self._heap[0][2] == _REMOVED:
            heapq.heappop(self._heap)
            self._stale_count -= 1

        if not self._heap:
            return None

        priority, item_id, _ = self._heap[0]
        return priority, item_id

    def items_at_or_below(self, threshold):
        """Return every live (priority, item_id) with priority <=
        threshold, ascending by priority.

        O(n) to scan the heap for matches plus O(k log k) to sort the
        k matches -- versus sorting/popping the entire structure, this
        only pays the log-factor for entries that are actually
        low-stock.
        """
        matches = [
            (entry[0], entry[1])
            for entry in self._heap
            if entry[2] == _LIVE and entry[0] <= threshold
        ]
        matches.sort()
        return matches

    def _mark_removed(self, item_id):
        entry = self._entry_finder.pop(item_id, None)
        if entry is None:
            return False
        entry[2] = _REMOVED
        self._live_count -= 1
        self._stale_count += 1
        return True

    def _compact(self):
        """Rebuild the heap keeping only live entries, and reset the
        stale counter. O(n log n), triggered only occasionally.
        """
        live_entries = [
            [priority, item_id, _LIVE]
            for priority, item_id, status in self._heap
            if status == _LIVE
        ]
        heapq.heapify(live_entries)
        self._heap = live_entries
        self._entry_finder = {entry[1]: entry for entry in live_entries}
        self._stale_count = 0
