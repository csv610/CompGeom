"""Spatial index data structures."""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import Point


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


__all__ = ["KDNode", "PointQuadtree", "QuadNode", "build_kdtree", "display_kdtree"]
