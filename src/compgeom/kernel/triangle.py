from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING, Tuple, List, Any
from decimal import Decimal

if TYPE_CHECKING:
    from .geometry import Point

from .math_utils import (
    EPSILON, 
    cross_product, 
    distance,
)

def _decimal_orientation(a: Point, b: Point, c: Point) -> Decimal:
    ax, ay = Decimal(a.x), Decimal(a.y)
    bx, by = Decimal(b.x), Decimal(b.y)
    cx, cy = Decimal(c.x), Decimal(c.y)
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def orientation(a: Point, b: Point, c: Point) -> float:
    """Return the signed orientation determinant of the triangle ABC."""
    value = cross_product(a, b, c)
    if abs(value) > EPSILON:
        return value
    return float(_decimal_orientation(a, b, c))


def orientation_sign(a: Point, b: Point, c: Point) -> int:
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


def area(a: Point, b: Point, c: Point) -> float:
    """Return the signed area of triangle ABC."""
    return 0.5 * cross_product(a, b, c)


def circumcenter(a: Point, b: Point, c: Point) -> Optional[Point]:
    """Return the circumcenter of triangle ABC, or None if collinear."""
    from .geometry import Point
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
    return Point(ux, uy)


def incenter(a: Point, b: Point, c: Point) -> Point:
    """Return the incenter of triangle ABC."""
    from .geometry import Point
    la = distance(b, c)
    lb = distance(a, c)
    lc = distance(a, b)
    perimeter = la + lb + lc
    if perimeter < EPSILON:
        return a
    return Point(
        (la * a.x + lb * b.x + lc * c.x) / perimeter,
        (la * a.y + lb * b.y + lc * c.y) / perimeter
    )


def inradius(a: Point, b: Point, c: Point) -> float:
    """Return the inradius of triangle ABC."""
    la = distance(b, c)
    lb = distance(a, c)
    lc = distance(a, b)
    s = (la + lb + lc) / 2.0
    area_val = abs(area(a, b, c))
    if s < EPSILON:
        return 0.0
    return area_val / s


def contains_point(a: Any, b: Any = None, c: Point | None = None, d: Point | None = None) -> bool:
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
    "area",
    "circumcenter",
    "incenter",
    "inradius",
    "contains_point",
    "orientation",
    "orientation_sign",
]
