"""Mathematical utilities and geometric primitives."""

from __future__ import annotations

import math
import fractions
from decimal import getcontext
from typing import TYPE_CHECKING, List, Optional, Tuple

from compgeom.kernel.point import EPSILON, Point2D, Point3D

# Set precision once for the module
getcontext().prec = 50


def cross_product(origin: Point2D, a: Point2D, b: Point2D) -> float:
    """Return the signed area of OA x OB."""
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x)


def dot_product(a: Point2D, b: Point2D) -> float:
    return a.x * b.x + a.y * b.y


def sub(a: Point2D, b: Point2D) -> Point2D:
    return Point2D(a.x - b.x, a.y - b.y)


def length_sq(point: Point2D) -> float:
    return point.x**2 + point.y**2


def length(point: Point2D) -> float:
    return math.hypot(point.x, point.y)


def distance(a: Point2D, b: Point2D) -> float:
    """Return the Euclidean distance between two 2D points."""
    return math.hypot(a.x - b.x, a.y - b.y)


def distance_3d(a: Point3D, b: Point3D) -> float:
    """Return the Euclidean distance between two 3D points."""
    return math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))


def signed_area_twice(polygon: List[Point2D]) -> float:
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


def rotate_2d(point: Point2D, cos_theta: float, sin_theta: float) -> Point2D:
    """Rotate a point by an angle given by its cosine and sine."""
    return Point2D(
        point.x * cos_theta + point.y * sin_theta,
        -point.x * sin_theta + point.y * cos_theta,
        point.id,
    )


def unrotate_2d(point: Point2D, cos_theta: float, sin_theta: float) -> Point2D:
    """Unrotate a point by an angle given by its cosine and sine."""
    return Point2D(
        point.x * cos_theta - point.y * sin_theta,
        point.x * sin_theta + point.y * cos_theta,
        point.id,
    )




def hilbert_key(x: int, y: int, n: int) -> int:
    """Calculate Hilbert curve order for a point in a n x n grid (n is power of 2)."""
    d = 0
    s = n // 2
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * ((3 * rx) ^ ry)
        # Rotate/Flip
        if ry == 0:
            if rx == 1:
                x = s - 1 - x
                y = s - 1 - y
            x, y = y, x
        s //= 2
    return d

def robust_orientation(a: Point2D, b: Point2D, p: Point2D) -> float:
    """Adaptive exact cross product (orientation) with SOS tie-breaking."""
    from compgeom.kernel.predicates import orient2d
    res = orient2d(a, b, p)
    if res != 0:
        return float(res)
        
    # Consistent tie-break using IDs
    return 1e-15 if (a.id < b.id) else -1e-15

def support(polygon: List[Point2D], direction: Point2D) -> Point2D:
    """Return the point in the polygon that is furthest in the given direction."""
    return max(polygon, key=lambda point: dot_product(point, direction))


__all__ = [
    "hilbert_key",
    "robust_orientation",
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
