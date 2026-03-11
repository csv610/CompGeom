from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING, Tuple, List
from decimal import Decimal

if TYPE_CHECKING:
    from .geometry import Point

from .math_utils import (
    EPSILON, 
    distance,
)

# Robust decimal incircle predicate helper
def _decimal_incircle(a: Point, b: Point, c: Point, d: Point) -> Decimal:
    adx_d = Decimal(a.x) - Decimal(d.x)
    ady_d = Decimal(a.y) - Decimal(d.y)
    bdx_d = Decimal(b.x) - Decimal(d.x)
    bdy_d = Decimal(b.y) - Decimal(d.y)
    cdx_d = Decimal(c.x) - Decimal(d.x)
    cdy_d = Decimal(c.y) - Decimal(d.y)
    return (
        (adx_d * adx_d + ady_d * ady_d) * (bdx_d * cdy_d - cdx_d * bdy_d)
        - (bdx_d * bdx_d + bdy_d * bdy_d) * (adx_d * cdy_d - cdx_d * ady_d)
        + (cdx_d * cdx_d + cdy_d * cdy_d) * (adx_d * bdy_d - bdx_d * ady_d)
    )

def incircle_det(a: Point, b: Point, c: Point, d: Point) -> float:
    """Return the determinant for the incircle test."""
    adx, ady = a.x - d.x, a.y - d.y
    bdx, bdy = b.x - d.x, b.y - d.y
    cdx, cdy = c.x - d.x, c.y - d.y

    determinant = (
        (adx * adx + ady * ady) * (bdx * cdy - cdx * bdy)
        - (bdx * bdx + bdy * bdy) * (adx * cdy - cdx * ady)
        + (cdx * cdx + cdy * cdy) * (adx * bdy - bdx * ady)
    )
    if abs(determinant) > EPSILON:
        return determinant
    return float(_decimal_incircle(a, b, c, d))


def incircle_sign(a: Point, b: Point, c: Point, d: Point) -> int:
    """Return the sign of the incircle test (1: inside, -1: outside, 0: on)."""
    from .triangle import orientation_sign
    determinant = incircle_det(a, b, c, d)
    orient = orientation_sign(a, b, c)
    adjusted = determinant * orient
    if adjusted > EPSILON:
        return 1
    if adjusted < -EPSILON:
        return -1
    exact = _decimal_incircle(a, b, c, d)
    if orient < 0:
        exact = -exact
    if exact > 0:
        return 1
    if exact < 0:
        return -1
    return 0


def in_circle(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Test if point d is inside the circumcircle of triangle ABC."""
    return incircle_sign(a, b, c, d) > 0


def from_two_points(p1: Point, p2: Point) -> tuple[Point, float]:
    """Return the smallest enclosing circle defined by two points."""
    from .geometry import Point
    center = Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
    return center, distance(p1, p2) / 2.0


def from_three_points(p1: Point, p2: Point, p3: Point) -> tuple[Point, float]:
    """Return the circumcircle defined by three points."""
    from .triangle import circumcenter
    center = circumcenter(p1, p2, p3)
    if center is None:
        # Collinear fallback: smallest circle of two furthest points
        d12 = distance(p1, p2)
        d13 = distance(p1, p3)
        d23 = distance(p2, p3)
        if d12 >= d13 and d12 >= d23:
            return from_two_points(p1, p2)
        if d13 >= d12 and d13 >= d23:
            return from_two_points(p1, p3)
        return from_two_points(p2, p3)
    return center, distance(center, p1)


def area(radius: float) -> float:
    """Return the area of a circle with given radius."""
    return math.pi * radius**2


def perimeter(radius: float) -> float:
    """Return the perimeter (circumference) of a circle with given radius."""
    return 2 * math.pi * radius


__all__ = [
    "incircle_det",
    "incircle_sign",
    "in_circle",
    "from_two_points",
    "from_three_points",
    "area",
    "perimeter",
]
