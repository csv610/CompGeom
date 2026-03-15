from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from .point import Point2D
from .math_utils import EPSILON, cross_product, signed_area_twice


@dataclass(frozen=True, slots=True)
class Polygon2D:
    """A general polygon defined by a list of 2D vertices."""
    vertices: Tuple[Point2D, ...]

    def __post_init__(self):
        if len(self.vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices.")

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    def area(self) -> float:
        """Return the area of the polygon."""
        return abs(signed_area_twice(list(self.vertices))) * 0.5

    def signed_area(self) -> float:
        """Return the signed area of the polygon (positive for CCW)."""
        return signed_area_twice(list(self.vertices)) * 0.5

    def centroid(self) -> Point2D:
        """Return the centroid (center of mass) of the polygon."""
        area_sum = 0.0
        cx = 0.0
        cy = 0.0
        n = self.num_vertices
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            cross = p1.x * p2.y - p2.x * p1.y
            area_sum += cross
            cx += (p1.x + p2.x) * cross
            cy += (p1.y + p2.y) * cross
        
        if abs(area_sum) < EPSILON:
            return self.vertices[0]
            
        return Point2D(cx / (3.0 * area_sum), cy / (3.0 * area_sum))

    def is_ccw(self) -> bool:
        """Return True if the vertices are in counter-clockwise order."""
        return signed_area_twice(list(self.vertices)) > 0

    def is_convex(self) -> bool:
        """Check if the polygon is convex."""
        n = self.num_vertices
        if n < 3:
            return False
            
        signs = []
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            p3 = self.vertices[(i + 2) % n]
            cp = (p2.x - p1.x) * (p3.y - p2.y) - (p2.y - p1.y) * (p3.x - p2.x)
            if abs(cp) > EPSILON:
                signs.append(cp > 0)
        
        if not signs:
            return True # All points collinear
            
        return all(s == signs[0] for s in signs)

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is inside the polygon using the ray-casting algorithm."""
        inside = False
        n = self.num_vertices
        j = n - 1
        for i in range(n):
            pi = self.vertices[i]
            pj = self.vertices[j]
            if ((pi.y > point.y) != (pj.y > point.y)) and \
               (point.x < (pj.x - pi.x) * (point.y - pi.y) / (pj.y - pi.y + 1e-18) + pi.x):
                inside = not inside
            j = i
        return inside

    def __repr__(self) -> str:
        return f"Polygon2D(n={self.num_vertices})"


__all__ = ["Polygon2D"]
