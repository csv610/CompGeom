"""Mathematical utilities and geometric primitives."""

from __future__ import annotations

import math
from decimal import getcontext
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from .geometry import Point, Point3D

EPSILON = 1e-9

# Set precision once for the module
getcontext().prec = 50


def cross_product(origin: Point, a: Point, b: Point) -> float:
    """Return the signed area of OA x OB."""
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x)


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


__all__ = [
    "EPSILON",
    "cross_product",
    "distance",
    "distance_3d",
    "dot_product",
    "length",
    "length_sq",
    "rotate_2d",
    "signed_area_twice",
    "sub",
    "support",
    "unrotate_2d",
]
