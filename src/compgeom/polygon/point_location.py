from __future__ import annotations
import random
from typing import List, Tuple, Optional, Union, Dict
from compgeom.kernel.point import Point2D
from compgeom.kernel.math_utils import EPSILON

class Trapezoid:
    """A trapezoid in the trapezoidal map."""
    def __init__(self, left: Point2D, right: Point2D, top_edge: Tuple[Point2D, Point2D], bottom_edge: Tuple[Point2D, Point2D]):
        self.left = left
        self.right = right
        self.top_edge = top_edge
        self.bottom_edge = bottom_edge
        # Neighbors
        self.upper_left: Optional[Trapezoid] = None
        self.lower_left: Optional[Trapezoid] = None
        self.upper_right: Optional[Trapezoid] = None
        self.lower_right: Optional[Trapezoid] = None
        # Reference to the node in the search structure
        self.node: Optional[TrapezoidNode] = None

class TrapezoidNode:
    """A node in the search structure (DAG) for the trapezoidal map."""
    def __init__(self, value: Union[Point2D, Tuple[Point2D, Point2D], Trapezoid]):
        self.value = value
        self.left_child: Optional[TrapezoidNode] = None
        self.right_child: Optional[TrapezoidNode] = None

    def is_leaf(self) -> bool:
        return isinstance(self.value, Trapezoid)

    def is_x_node(self) -> bool:
        return isinstance(self.value, Point2D)

    def is_y_node(self) -> bool:
        return isinstance(self.value, tuple)

class TrapezoidalMap:
    """
    A randomized incremental trapezoidal map for O(log n) point location.
    """
    def __init__(self, bbox: Tuple[Point2D, Point2D]):
        # Initialize with a large bounding trapezoid
        p1, p2 = bbox
        self.bounding_box = bbox
        # Define top and bottom edges of the universe
        top_edge = (Point2D(p1.x, p2.y), p2)
        bottom_edge = (p1, Point2D(p2.x, p1.y))
        
        root_trap = Trapezoid(p1, p2, top_edge, bottom_edge)
        self.root = TrapezoidNode(root_trap)
        root_trap.node = self.root
        self.trapezoids: List[Trapezoid] = [root_trap]

    def locate(self, point: Point2D) -> Optional[Trapezoid]:
        """Finds the trapezoid containing the point in O(log n) time."""
        curr = self.root
        while not curr.is_leaf():
            if curr.is_x_node():
                if point.x < curr.value.x:
                    curr = curr.left_child
                else:
                    curr = curr.right_child
            else:
                if self._is_above(point, curr.value):
                    curr = curr.left_child
                else:
                    curr = curr.right_child
        return curr.value

    def _is_above(self, p: Point2D, edge: Tuple[Point2D, Point2D]) -> bool:
        p1, p2 = edge
        return (p2.x - p1.x) * (p.y - p1.y) - (p2.y - p1.y) * (p.x - p1.x) > 0
