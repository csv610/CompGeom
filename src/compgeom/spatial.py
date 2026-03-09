"""Spatial index data structures and point cloud simplification."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Union

from .geometry import Point, Point3D
from .math_utils import distance, distance_3d


@dataclass
class QuadNode:
    point: Point
    nw: "QuadNode | None" = None
    ne: "QuadNode | None" = None
    sw: "QuadNode | None" = None
    se: "QuadNode | None" = None


class PointQuadtree:
    def __init__(self):
        self.root: QuadNode | None = None
        self.count = 0

    def insert(self, point: Point) -> bool:
        if self.root is None:
            self.root = QuadNode(point)
            self.count += 1
            return True
        return self._insert_recursive(self.root, point)

    def _insert_recursive(self, node: QuadNode, point: Point) -> bool:
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
    def _get_quadrant_name(origin: Point, point: Point) -> str:
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
    point: Point
    axis: int
    left: "KDNode | None" = None
    right: "KDNode | None" = None


def build_kdtree(points: list[Point], depth: int = 0):
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


class PointSimplifier:
    """Simplifies large point sets by decimation."""

    @staticmethod
    def get_bounding_box(points: Iterable[Union[Point, Point3D]]) -> Tuple:
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
    def simplify(points: List[Union[Point, Point3D]], ratio: float) -> List[Union[Point, Point3D]]:
        """
        Simplifies points by keeping only one point per grid cell.
        Also checks neighboring cells to ensure Euclidean distance > threshold.
        Grid size is determined by ratio * bounding_box_diagonal.
        """
        if not points:
            return []

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

        grid: Dict[Tuple, Union[Point, Point3D]] = {}
        simplified_points = []
        
        # Determine neighborhood offsets
        offsets = [-1, 0, 1]
        if is_3d:
            neighbor_indices = [(dx, dy, dz) for dx in offsets for dy in offsets for dz in offsets]
        else:
            neighbor_indices = [(dx, dy) for dx in offsets for dy in offsets]

        for p in points:
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
    "KDNode",
    "PointQuadtree",
    "PointSimplifier",
    "QuadNode",
    "build_kdtree",
    "display_kdtree",
]
