from typing import TypeVar, Generic, Set
from queue import PriorityQueue
from dataclasses import dataclass

T = TypeVar('T')

class EnhancedPriorityQueue(Generic[T]):
    """Priority Queue with efficient membership testing."""

    def __init__(self):
        self._queue = PriorityQueue()
        self._items: Set[T] = set()

    def put(self, priority: float, item: T) -> None:
        """Add an item with given priority."""
        if item not in self._items:
            self._queue.put((priority, id(item), item))
            self._items.add(item)

    def get(self) -> T:
        """Get the item with lowest priority."""
        _, _, item = self._queue.get()
        self._items.remove(item)
        return item

    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()

    def has_item(self, item: T) -> bool:
        """Check if item exists in queue."""
        return item in self._items
