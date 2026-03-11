"""Mathematical utilities and geometric primitives."""

from __future__ import annotations

import math
from decimal import Decimal, getcontext
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from .geometry import Point, Point3D

EPSILON = 1e-9

# Set precision once for the module
getcontext().prec = 50


def _decimal_orientation(a: Point, b: Point, c: Point) -> Decimal:
    ax, ay = Decimal(a.x), Decimal(a.y)
    bx, by = Decimal(b.x), Decimal(b.y)
    cx, cy = Decimal(c.x), Decimal(c.y)
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


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


def cross_product(origin: Point, a: Point, b: Point) -> float:
    """Return the signed area of OA x OB."""
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x)


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


def dot_product(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def sub(a: Point, b: Point) -> Point:
    from .geometry import Point

    return Point(a.x - b.x, a.y - b.y)


def length_sq(point: Point) -> float:
    return point.x**2 + point.y**2


def length(point: Point) -> float:
    return math.hypot(point.x, point.y)


def distance(a: Point, b: Point) -> float:
    """Return the Euclidean distance between two 2D points."""
    return math.hypot(a.x - b.x, a.y - b.y)


def distance_3d(a: Point3D, b: Point3D) -> float:
    """Return the Euclidean distance between two 3D points."""
    return math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))


def signed_area_twice(polygon: List[Point]) -> float:
    """Return twice the signed area of a polygon."""
    n = len(polygon)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n - 1):
        p1 = polygon[i]
        p2 = polygon[i + 1]
        area += p1.x * p2.y - p2.x * p1.y
    # Closing the polygon
    area += polygon[n - 1].x * polygon[0].y - polygon[0].x * polygon[n - 1].y
    return area


def rotate_2d(point: Point, cos_theta: float, sin_theta: float) -> Point:
    """Rotate a point by an angle given by its cosine and sine."""
    from .geometry import Point

    return Point(
        point.x * cos_theta + point.y * sin_theta,
        -point.x * sin_theta + point.y * cos_theta,
        point.id,
    )


def unrotate_2d(point: Point, cos_theta: float, sin_theta: float) -> Point:
    """Unrotate a point by an angle given by its cosine and sine."""
    from .geometry import Point

    return Point(
        point.x * cos_theta - point.y * sin_theta,
        point.x * sin_theta + point.y * cos_theta,
        point.id,
    )


def support(polygon: List[Point], direction: Point) -> Point:
    """Return the point in the polygon that is furthest in the given direction."""
    return max(polygon, key=lambda point: dot_product(point, direction))


def get_circle_two_points(p1: Point, p2: Point) -> tuple[Point, float]:
    """Return the smallest enclosing circle defined by two points."""
    from .geometry import Point

    center = Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
    return center, distance(p1, p2) / 2.0


def get_circle_three_points(p1: Point, p2: Point, p3: Point) -> tuple[Point, float]:
    """Return the smallest enclosing circle defined by three points."""
    from .geometry import get_circumcenter

    center = get_circumcenter(p1, p2, p3)
    if center is None:
        d12 = distance(p1, p2)
        d13 = distance(p1, p3)
        d23 = distance(p2, p3)
        if d12 >= d13 and d12 >= d23:
            return get_circle_two_points(p1, p2)
        if d13 >= d12 and d13 >= d23:
            return get_circle_two_points(p1, p3)
        return get_circle_two_points(p2, p3)
    return center, distance(center, p1)


def incircle_det(a: Point, b: Point, c: Point, d: Point) -> float:
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
    return incircle_sign(a, b, c, d) > 0

__all__ = [
    "EPSILON",
    "cross_product",
    "distance",
    "distance_3d",
    "dot_product",
    "get_circle_three_points",
    "get_circle_two_points",
    "in_circle",
    "incircle_det",
    "incircle_sign",
    "length",
    "length_sq",
    "orientation",
    "orientation_sign",
    "rotate_2d",
    "signed_area_twice",
    "sub",
    "support",
    "unrotate_2d",
]
