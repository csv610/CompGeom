"""Spatial index data structures and point cloud simplification."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Generic, Iterable, List, Optional, Sequence, Set, Tuple, TypeVar, Union

from ..kernel import Point2D, Point3D
from ..kernel import distance, distance_3d

T = TypeVar("T")


@dataclass
class QuadNode:
    point: Point2D
    nw: "QuadNode | None" = None
    ne: "QuadNode | None" = None
    sw: "QuadNode | None" = None
    se: "QuadNode | None" = None


class PointQuadtree:
    def __init__(self):
        self.root: QuadNode | None = None
        self.count = 0

    def insert(self, point: Point2D) -> bool:
        if self.root is None:
            self.root = QuadNode(point)
            self.count += 1
            return True
        return self._insert_recursive(self.root, point)

    def _insert_recursive(self, node: QuadNode, point: Point2D) -> bool:
        if point.x == node.point.x and point.y == node.point.y:
            return False

        quadrant_name = self._get_quadrant_name(node.point, point)
        child = getattr(node, quadrant_name)
        if child is None:
            setattr(node, quadrant_name, QuadNode(point))
            self.count += 1
            return True
        return self._insert_recursive(child, point)

    @staticmethod
    def _get_quadrant_name(origin: Point2D, point: Point2D) -> str:
        if point.x >= origin.x:
            return "ne" if point.y >= origin.y else "se"
        return "nw" if point.y >= origin.y else "sw"

    def display(self):
        self._display_recursive(self.root, 0, "Root")

    def _display_recursive(self, node: QuadNode | None, depth: int, label: str):
        if node is None:
            return
        print(f"{'  ' * depth}{label}: {node.point}")
        self._display_recursive(node.nw, depth + 1, "NW")
        self._display_recursive(node.ne, depth + 1, "NE")
        self._display_recursive(node.sw, depth + 1, "SW")
        self._display_recursive(node.se, depth + 1, "SE")


@dataclass
class KDNode:
    point: Point2D
    axis: int
    left: "KDNode | None" = None
    right: "KDNode | None" = None


def build_kdtree(points: list[Point2D], depth: int = 0):
    if not points:
        return None

    axis = depth % 2
    ordered = sorted(points, key=lambda point: point.x if axis == 0 else point.y)
    median_index = len(ordered) // 2
    return KDNode(
        point=ordered[median_index],
        axis=axis,
        left=build_kdtree(ordered[:median_index], depth + 1),
        right=build_kdtree(ordered[median_index + 1 :], depth + 1),
    )


def display_kdtree(node: KDNode | None, depth: int = 0):
    if node is None:
        return
    print(f"{'  ' * depth}[Depth {depth}, Split {'X' if node.axis == 0 else 'Y'}] {node.point}")
    display_kdtree(node.left, depth + 1)
    display_kdtree(node.right, depth + 1)


def range_search(
    node: KDNode | None,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
) -> list[Point2D]:
    """Return points inside an axis-aligned query rectangle from a KD-tree."""
    if node is None:
        return []

    point = node.point
    result: list[Point2D] = []
    if min_x <= point.x <= max_x and min_y <= point.y <= max_y:
        result.append(point)

    split_value = point.x if node.axis == 0 else point.y
    lower_bound = min_x if node.axis == 0 else min_y
    upper_bound = max_x if node.axis == 0 else max_y

    if lower_bound <= split_value:
        result.extend(range_search(node.left, min_x, max_x, min_y, max_y))
    if split_value <= upper_bound:
        result.extend(range_search(node.right, min_x, max_x, min_y, max_y))
    return result


@dataclass(frozen=True, slots=True)
class Interval:
    start: float
    end: float
    payload: object | None = None

    def __post_init__(self):
        if self.end < self.start:
            raise ValueError("Interval end must be greater than or equal to start.")

    def overlaps(self, start: float, end: float) -> bool:
        return not (self.end < start or end < self.start)

    def contains(self, value: float) -> bool:
        return self.start <= value <= self.end


@dataclass(slots=True)
class IntervalTreeNode:
    center: float
    intervals: list[Interval]
    left: "IntervalTreeNode | None" = None
    right: "IntervalTreeNode | None" = None


class IntervalTree:
    """Centered interval tree supporting stabbing and overlap queries."""

    def __init__(self, intervals: Iterable[Interval | tuple[float, float] | tuple[float, float, object]] = ()):
        normalized = [self._normalize_interval(interval) for interval in intervals]
        self.root = self._build(normalized)

    @staticmethod
    def _normalize_interval(interval: Interval | tuple[float, float] | tuple[float, float, object]) -> Interval:
        if isinstance(interval, Interval):
            return interval
        if len(interval) == 2:
            start, end = interval
            return Interval(start, end)
        start, end, payload = interval
        return Interval(start, end, payload)

    def _build(self, intervals: list[Interval]) -> IntervalTreeNode | None:
        if not intervals:
            return None

        endpoints = sorted([value for interval in intervals for value in (interval.start, interval.end)])
        center = endpoints[len(endpoints) // 2]
        overlapping = [interval for interval in intervals if interval.contains(center)]
        left = [interval for interval in intervals if interval.end < center]
        right = [interval for interval in intervals if interval.start > center]
        overlapping.sort(key=lambda interval: (interval.start, interval.end))
        return IntervalTreeNode(
            center=center,
            intervals=overlapping,
            left=self._build(left),
            right=self._build(right),
        )

    def query_point(self, value: float) -> list[Interval]:
        result: list[Interval] = []
        self._query_point(self.root, value, result)
        return result

    def _query_point(self, node: IntervalTreeNode | None, value: float, result: list[Interval]) -> None:
        if node is None:
            return
        result.extend(interval for interval in node.intervals if interval.contains(value))
        if value < node.center:
            self._query_point(node.left, value, result)
        elif value > node.center:
            self._query_point(node.right, value, result)

    def query_interval(self, start: float, end: float) -> list[Interval]:
        if end < start:
            raise ValueError("Query interval end must be greater than or equal to start.")
        result: list[Interval] = []
        self._query_interval(self.root, start, end, result)
        return result

    def _query_interval(
        self, node: IntervalTreeNode | None, start: float, end: float, result: list[Interval]
    ) -> None:
        if node is None:
            return
        result.extend(interval for interval in node.intervals if interval.overlaps(start, end))
        if start <= node.center:
            self._query_interval(node.left, start, end, result)
        if node.center <= end:
            self._query_interval(node.right, start, end, result)


class SegmentTree(Generic[T]):
    """Array-backed segment tree with configurable range aggregation."""

    def __init__(
        self,
        values: Sequence[T],
        combine: Callable[[T, T], T] | None = None,
        default: T | None = None,
    ):
        if not values:
            raise ValueError("SegmentTree requires at least one value.")
        if combine is None:
            combine = lambda left, right: left + right
        if default is None:
            default = 0  # type: ignore[assignment]

        self.combine = combine
        self.default = default
        self.size = len(values)
        self.tree: list[T] = [self.default for _ in range(4 * self.size)]
        self._build(1, 0, self.size - 1, list(values))

    def _build(self, node: int, left: int, right: int, values: list[T]) -> None:
        if left == right:
            self.tree[node] = values[left]
            return
        mid = (left + right) // 2
        self._build(node * 2, left, mid, values)
        self._build(node * 2 + 1, mid + 1, right, values)
        self.tree[node] = self.combine(self.tree[node * 2], self.tree[node * 2 + 1])

    def update(self, index: int, value: T) -> None:
        if not 0 <= index < self.size:
            raise IndexError("SegmentTree index out of range.")
        self._update(1, 0, self.size - 1, index, value)

    def _update(self, node: int, left: int, right: int, index: int, value: T) -> None:
        if left == right:
            self.tree[node] = value
            return
        mid = (left + right) // 2
        if index <= mid:
            self._update(node * 2, left, mid, index, value)
        else:
            self._update(node * 2 + 1, mid + 1, right, index, value)
        self.tree[node] = self.combine(self.tree[node * 2], self.tree[node * 2 + 1])

    def range_query(self, query_left: int, query_right: int) -> T:
        if not 0 <= query_left <= query_right < self.size:
            raise IndexError("SegmentTree query range out of bounds.")
        return self._range_query(1, 0, self.size - 1, query_left, query_right)

    def _range_query(self, node: int, left: int, right: int, query_left: int, query_right: int) -> T:
        if query_left <= left and right <= query_right:
            return self.tree[node]
        if right < query_left or query_right < left:
            return self.default

        mid = (left + right) // 2
        left_value = self._range_query(node * 2, left, mid, query_left, query_right)
        right_value = self._range_query(node * 2 + 1, mid + 1, right, query_left, query_right)
        return self.combine(left_value, right_value)

    @classmethod
    def for_sum(cls, values: Sequence[float | int]) -> "SegmentTree[float | int]":
        return cls(values, combine=lambda left, right: left + right, default=0)

    @classmethod
    def for_min(cls, values: Sequence[float | int]) -> "SegmentTree[float | int]":
        return cls(values, combine=min, default=float("inf"))

    @classmethod
    def for_max(cls, values: Sequence[float | int]) -> "SegmentTree[float | int]":
        return cls(values, combine=max, default=float("-inf"))


class PointSimplifier:
    """Simplifies large point sets by decimation."""

    @staticmethod
    def get_bounding_box(points: Iterable[Union[Point2D, Point3D]]) -> Tuple:
        """Finds the axis-aligned bounding box for a set of points."""
        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")
        is_3d = False

        for p in points:
            if p.x < min_x: min_x = p.x
            if p.x > max_x: max_x = p.x
            if p.y < min_y: min_y = p.y
            if p.y > max_y: max_y = p.y
            if isinstance(p, Point3D):
                is_3d = True
                if p.z < min_z: min_z = p.z
                if p.z > max_z: max_z = p.z

        if not is_3d:
            return (min_x, max_x, min_y, max_y), False
        return (min_x, max_x, min_y, max_y, min_z, max_z), True

    @staticmethod
    def simplify(
        points: List[Union[Point2D, Point3D]], 
        ratio: float,
        protected_ids: Optional[Set[int]] = None
    ) -> List[Union[Point2D, Point3D]]:
        """
        Simplifies points by keeping only one point per grid cell.
        Also checks neighboring cells to ensure Euclidean distance > threshold.
        Grid size is determined by ratio * bounding_box_diagonal.
        
        Points with IDs in protected_ids are never removed.
        """
        if not points:
            return []

        protected = protected_ids or set()
        bbox, is_3d = PointSimplifier.get_bounding_box(points)
        
        if is_3d:
            min_x, max_x, min_y, max_y, min_z, max_z = bbox
            diagonal = math.sqrt((max_x - min_x)**2 + (max_y - min_y)**2 + (max_z - min_z)**2)
        else:
            min_x, max_x, min_y, max_y = bbox
            diagonal = math.sqrt((max_x - min_x)**2 + (max_y - min_y)**2)

        threshold = ratio * diagonal
        if threshold <= 0:
            return points

        grid: Dict[Tuple, Union[Point2D, Point3D]] = {}
        simplified_points = []
        
        # Determine neighborhood offsets
        offsets = [-1, 0, 1]
        if is_3d:
            neighbor_indices = [(dx, dy, dz) for dx in offsets for dy in offsets for dz in offsets]
        else:
            neighbor_indices = [(dx, dy) for dx in offsets for dy in offsets]

        for p in points:
            # Always keep protected points
            if p.id in protected:
                simplified_points.append(p)
                # Register in grid so others don't get too close
                if is_3d:
                    key = (int(p.x / threshold), int(p.y / threshold), int(p.z / threshold))
                else:
                    key = (int(p.x / threshold), int(p.y / threshold))
                grid[key] = p
                continue

            if is_3d:
                gx, gy, gz = int(p.x / threshold), int(p.y / threshold), int(p.z / threshold)
                key = (gx, gy, gz)
                
                is_too_close = False
                for dx, dy, dz in neighbor_indices:
                    neighbor_key = (gx + dx, gy + dy, gz + dz)
                    if neighbor_key in grid:
                        if distance_3d(p, grid[neighbor_key]) < threshold:
                            is_too_close = True
                            break
                
                if not is_too_close:
                    grid[key] = p
                    simplified_points.append(p)
            else:
                gx, gy = int(p.x / threshold), int(p.y / threshold)
                key = (gx, gy)
                
                is_too_close = False
                for dx, dy in neighbor_indices:
                    neighbor_key = (gx + dx, gy + dy)
                    if neighbor_key in grid:
                        if distance(p, grid[neighbor_key]) < threshold:
                            is_too_close = True
                            break
                
                if not is_too_close:
                    grid[key] = p
                    simplified_points.append(p)
                
        return simplified_points


__all__ = [
    "Interval",
    "IntervalTree",
    "IntervalTreeNode",
    "KDNode",
    "PointQuadtree",
    "PointSimplifier",
    "QuadNode",
    "SegmentTree",
    "build_kdtree",
    "display_kdtree",
    "range_search",
]
