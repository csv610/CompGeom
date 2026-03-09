"""Mathematical utilities and geometric primitives."""

from __future__ import annotations

import math
from decimal import Decimal, getcontext
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from .geometry import Point

EPSILON = 1e-9


def _decimal_orientation(a: Point, b: Point, c: Point) -> Decimal:
    getcontext().prec = 50
    ax = Decimal(str(a.x))
    ay = Decimal(str(a.y))
    bx = Decimal(str(b.x))
    by = Decimal(str(b.y))
    cx = Decimal(str(c.x))
    cy = Decimal(str(c.y))
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _decimal_incircle(a: Point, b: Point, c: Point, d: Point) -> Decimal:
    getcontext().prec = 50
    adx_d = Decimal(str(a.x)) - Decimal(str(d.x))
    ady_d = Decimal(str(a.y)) - Decimal(str(d.y))
    bdx_d = Decimal(str(b.x)) - Decimal(str(d.x))
    bdy_d = Decimal(str(b.y)) - Decimal(str(d.y))
    cdx_d = Decimal(str(c.x)) - Decimal(str(d.x))
    cdy_d = Decimal(str(c.y)) - Decimal(str(d.y))
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
    return length_sq(point) ** 0.5


def distance(a: Point, b: Point) -> float:
    """Return the Euclidean distance between two 2D points."""
    return length(sub(a, b))


def distance_3d(a: Point3D, b: Point3D) -> float:
    """Return the Euclidean distance between two 3D points."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def signed_area_twice(polygon: List[Point]) -> float:
    """Return twice the signed area of a polygon."""
    return sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


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


def peano_index_to_coords(index: int, level: int) -> Tuple[int, int]:
    """Convert a Peano curve index to 2D coordinates."""
    x = y = px = py = 0
    for power in range(level - 1, -1, -1):
        power_of_three = 3**power
        digit = (index // (9**power)) % 9
        row = digit // 3
        col = digit % 3 if row % 2 == 0 else 2 - (digit % 3)
        if py % 2 == 1:
            col = 2 - col
        if px % 2 == 1:
            row = 2 - row
        x += col * power_of_three
        y += row * power_of_three
        if col == 1:
            px += 1
        if row == 1:
            py += 1
    return x, y


def morton_index_to_coords(index: int) -> Tuple[int, int]:
    """Convert a Morton curve (Z-order) index to 2D coordinates."""
    x = y = 0
    for bit in range(32):
        x |= (index & (1 << (2 * bit))) >> bit
        y |= (index & (1 << (2 * bit + 1))) >> (bit + 1)
    return x, y


def hilbert_index_to_coords(index: int, order: int) -> Tuple[int, int]:
    """Convert a Hilbert curve index to 2D coordinates."""
    x = y = 0
    t = index
    for scale in range(order):
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = (2**scale - 1 - x), (2**scale - 1 - y)
            x, y = y, x
        x += rx * (2**scale)
        y += ry * (2**scale)
        t //= 4
    return x, y


__all__ = [
    "EPSILON",
    "cross_product",
    "distance",
    "distance_3d",
    "dot_product",
    "get_circle_three_points",
    "get_circle_two_points",
    "hilbert_index_to_coords",
    "in_circle",
    "incircle_det",
    "incircle_sign",
    "length",
    "length_sq",
    "morton_index_to_coords",
    "orientation",
    "orientation_sign",
    "peano_index_to_coords",
    "rotate_2d",
    "signed_area_twice",
    "sub",
    "support",
    "unrotate_2d",
]
