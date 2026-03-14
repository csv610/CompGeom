from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Tuple, List, Any
from decimal import Decimal

if TYPE_CHECKING:
    from .point import Point2D, Point3D

from .math_utils import (
    EPSILON, 
    cross_product, 
    distance,
)

@dataclass(frozen=True, slots=True)
class Triangle2D:
    v1: Point2D
    v2: Point2D
    v3: Point2D

    @property
    def vertices(self) -> Tuple[Point2D, Point2D, Point2D]:
        return (self.v1, self.v2, self.v3)

    def area(self) -> float:
        return area(self.v1, self.v2, self.v3)

    def orientation(self) -> float:
        return orientation(self.v1, self.v2, self.v3)

    def orientation_sign(self) -> int:
        return orientation_sign(self.v1, self.v2, self.v3)

    def circumcenter(self) -> Optional[Point2D]:
        return circumcenter(self.v1, self.v2, self.v3)

    def incenter(self) -> Point2D:
        return incenter(self.v1, self.v2, self.v3)

    def inradius(self) -> float:
        return inradius(self.v1, self.v2, self.v3)

    def contains_point(self, p: Point2D) -> bool:
        return contains_point(self.v1, self.v2, self.v3, p)

    def __repr__(self) -> str:
        return f"Triangle2D({self.v1}, {self.v2}, {self.v3})"

@dataclass(frozen=True, slots=True)
class Triangle3D:
    v1: Point3D
    v2: Point3D
    v3: Point3D

    @property
    def vertices(self) -> Tuple[Point3D, Point3D, Point3D]:
        return (self.v1, self.v2, self.v3)

    def normal(self) -> Point3D:
        edge1 = self.v2 - self.v1
        edge2 = self.v3 - self.v1
        n = edge1.cross(edge2)
        return n / n.length()

    def area(self) -> float:
        edge1 = self.v2 - self.v1
        edge2 = self.v3 - self.v1
        return 0.5 * edge1.cross(edge2).length()

    def __repr__(self) -> str:
        return f"Triangle3D({self.v1}, {self.v2}, {self.v3})"


def _decimal_orientation(a: Point2D, b: Point2D, c: Point2D) -> Decimal:
    ax, ay = Decimal(str(a.x)), Decimal(str(a.y))
    bx, by = Decimal(str(b.x)), Decimal(str(b.y))
    cx, cy = Decimal(str(c.x)), Decimal(str(c.y))
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def orientation(a: Point2D, b: Point2D, c: Point2D) -> float:
    """Return the signed orientation determinant of the triangle ABC."""
    value = cross_product(a, b, c)
    if abs(value) > EPSILON:
        return value
    return float(_decimal_orientation(a, b, c))


def orientation_sign(a: Point2D, b: Point2D, c: Point2D) -> int:
    value = orientation(a, b, c)
    if value > EPSILON:
        return 1
    if value < -EPSILON:
        return -1
    exact = _decimal_orientation(a, b, c)
    if exact > 0:
        return 1
    if exact < 0:
        return -1
    return 0


def area(a: Point2D, b: Point2D, c: Point2D) -> float:
    """Return the signed area of triangle ABC."""
    return 0.5 * cross_product(a, b, c)


def circumcenter(a: Point2D, b: Point2D, c: Point2D) -> Optional[Point2D]:
    """Return the circumcenter of triangle ABC, or None if collinear."""
    from .point import Point2D
    denominator = 2 * (
        a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)
    )
    if abs(denominator) < 1e-12:
        return None

    ux = (
        (a.x**2 + a.y**2) * (b.y - c.y)
        + (b.x**2 + b.y**2) * (c.y - a.y)
        + (c.x**2 + c.y**2) * (a.y - b.y)
    ) / denominator
    uy = (
        (a.x**2 + a.y**2) * (c.x - b.x)
        + (b.x**2 + b.y**2) * (a.x - c.x)
        + (c.x**2 + c.y**2) * (b.x - a.x)
    ) / denominator
    return Point2D(ux, uy)


def incenter(a: Point2D, b: Point2D, c: Point2D) -> Point2D:
    """Return the incenter of triangle ABC."""
    from .point import Point2D
    la = distance(b, c)
    lb = distance(a, c)
    lc = distance(a, b)
    perimeter = la + lb + lc
    if perimeter < EPSILON:
        return a
    return Point2D(
        (la * a.x + lb * b.x + lc * c.x) / perimeter,
        (la * a.y + lb * b.y + lc * c.y) / perimeter
    )


def inradius(a: Point2D, b: Point2D, c: Point2D) -> float:
    """Return the inradius of triangle ABC."""
    la = distance(b, c)
    lb = distance(a, c)
    lc = distance(a, b)
    s = (la + lb + lc) / 2.0
    area_val = abs(area(a, b, c))
    if s < EPSILON:
        return 0.0
    return area_val / s


def contains_point(a: Any, b: Any = None, c: Point2D | None = None, d: Point2D | None = None) -> bool:
    """
    Check if a point is inside a triangle.
    Supports both contains_point(triangle, point) and contains_point(v1, v2, v3, point).
    """
    if c is None:
        # Case: contains_point(triangle, point)
        v1, v2, v3 = a.vertices
        p = b
    else:
        # Case: contains_point(v1, v2, v3, point)
        v1, v2, v3, p = a, b, c, d

    cp1 = orientation(v1, v2, p)
    cp2 = orientation(v2, v3, p)
    cp3 = orientation(v3, v1, p)
    return (
        cp1 >= -EPSILON and cp2 >= -EPSILON and cp3 >= -EPSILON
    ) or (
        cp1 <= EPSILON and cp2 <= EPSILON and cp3 <= EPSILON
    )


__all__ = [
    "Triangle2D",
    "Triangle3D",
    "area",
    "circumcenter",
    "incenter",
    "inradius",
    "contains_point",
    "orientation",
    "orientation_sign",
]
