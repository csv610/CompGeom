"""Spatial Indexing using R-tree (inspired by Boost.Geometry)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, TypeVar, Generic

T = TypeVar("T")

@dataclass
class BoundingBox:
    """Axis-Aligned Bounding Box (AABB)."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @staticmethod
    def from_point(x: float, y: float, padding: float = 0.0) -> BoundingBox:
        return BoundingBox(x - padding, y - padding, x + padding, y + padding)

    def intersects(self, other: BoundingBox) -> bool:
        return not (
            self.max_x < other.min_x
            or self.min_x > other.max_x
            or self.max_y < other.min_y
            or self.min_y > other.max_y
        )

    def expand(self, other: BoundingBox) -> BoundingBox:
        return BoundingBox(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y),
        )

    def area(self) -> float:
        return max(0.0, self.max_x - self.min_x) * max(0.0, self.max_y - self.min_y)

class RTreeNode(Generic[T]):
    def __init__(self, is_leaf: bool, max_entries: int):
        self.is_leaf = is_leaf
        self.max_entries = max_entries
        self.entries: List[Tuple[BoundingBox, Optional[RTreeNode[T]], Optional[T]]] = []
        self.bbox: Optional[BoundingBox] = None

    def update_bbox(self):
        if not self.entries:
            self.bbox = None
            return
        self.bbox = self.entries[0][0]
        for i in range(1, len(self.entries)):
            self.bbox = self.bbox.expand(self.entries[i][0])

class RTree(Generic[T]):
    """A lightweight R-tree for 2D spatial indexing."""

    def __init__(self, max_entries: int = 16):
        self.max_entries = max_entries
        self.root = RTreeNode[T](is_leaf=True, max_entries=max_entries)

    def insert(self, bbox: BoundingBox, item: T):
        """Insert an item with its bounding box into the tree."""
        # Simple implementation for architectural demonstration
        node = self.root
        if node.is_leaf:
            node.entries.append((bbox, None, item))
            node.update_bbox()
        else:
            # Recursive descent (simplified)
            node.entries.append((bbox, None, item))
            node.update_bbox()

    def query(self, query_bbox: BoundingBox) -> List[T]:
        """Find all items whose bounding boxes intersect the query box."""
        results = []
        self._query(self.root, query_bbox, results)
        return results

    def _query(self, node: RTreeNode[T], query_bbox: BoundingBox, results: List[T]):
        if not node.bbox or not node.bbox.intersects(query_bbox):
            return

        for bbox, child, item in node.entries:
            if bbox.intersects(query_bbox):
                if node.is_leaf:
                    results.append(item)
                elif child:
                    self._query(child, query_bbox, results)
