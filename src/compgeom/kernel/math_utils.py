"""Mathematical utilities and geometric primitives."""

from __future__ import annotations

import math
import fractions
from decimal import getcontext
from typing import TYPE_CHECKING, List, Optional, Tuple

from compgeom.kernel.point import EPSILON, Point2D, Point3D
from compgeom.kernel.predicates import orient2d

# Set precision once for the module
getcontext().prec = 50


def cross_product(origin: Point2D, a: Point2D, b: Point2D) -> float:
    """Calculates the cross product of vectors OA and OB.

    Args:
        origin: The origin point O.
        a: Point A.
        b: Point B.

    Returns:
        The signed area of the parallelogram formed by OA and OB.
    """
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x)


def dot_product(a: Point2D, b: Point2D) -> float:
    """Calculates the dot product of two 2D points (vectors from origin).

    Args:
        a: The first point.
        b: The second point.

    Returns:
        The dot product of a and b.
    """
    return a.x * b.x + a.y * b.y


def sub(a: Point2D, b: Point2D) -> Point2D:
    """Subtracts one 2D point from another.

    Args:
        a: The point to subtract from.
        b: The point to subtract.

    Returns:
        A new Point2D representing the vector from b to a.
    """
    return Point2D(a.x - b.x, a.y - b.y)


def length_sq(point: Point2D) -> float:
    """Calculates the squared length of a 2D point (vector from origin).

    Args:
        point: The point.

    Returns:
        The squared Euclidean length.
    """
    return point.x**2 + point.y**2


def length(point: Point2D) -> float:
    """Calculates the Euclidean length of a 2D point (vector from origin).

    Args:
        point: The point.

    Returns:
        The Euclidean length.
    """
    return math.hypot(point.x, point.y)


def distance(a: Point2D, b: Point2D) -> float:
    """Calculates the Euclidean distance between two 2D points.

    Args:
        a: The first point.
        b: The second point.

    Returns:
        The Euclidean distance between a and b.
    """
    return math.hypot(a.x - b.x, a.y - b.y)


def distance_3d(a: Point3D, b: Point3D) -> float:
    """Calculates the Euclidean distance between two 3D points.

    Args:
        a: The first 3D point.
        b: The second 3D point.

    Returns:
        The Euclidean distance between a and b.
    """
    return math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))


def signed_area_twice(polygon: List[Point2D]) -> float:
    """Calculates twice the signed area of a polygon.

    Args:
        polygon: A list of 2D points representing the polygon vertices.

    Returns:
        Twice the signed area. Returns 0.0 if the polygon has fewer than 3 vertices.
    """
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
    """Rotates a point by an angle given by its cosine and sine.

    Args:
        point: The 2D point to rotate.
        cos_theta: The cosine of the rotation angle.
        sin_theta: The sine of the rotation angle.

    Returns:
        The rotated Point2D.
    """
    return Point2D(
        point.x * cos_theta + point.y * sin_theta,
        -point.x * sin_theta + point.y * cos_theta,
        point.id,
    )


def unrotate_2d(point: Point2D, cos_theta: float, sin_theta: float) -> Point2D:
    """Unrotates a point by an angle given by its cosine and sine.

    Args:
        point: The 2D point to unrotate.
        cos_theta: The cosine of the original rotation angle.
        sin_theta: The sine of the original rotation angle.

    Returns:
        The unrotated Point2D.
    """
    return Point2D(
        point.x * cos_theta - point.y * sin_theta,
        point.x * sin_theta + point.y * cos_theta,
        point.id,
    )


def hilbert_key(x: int, y: int, n: int) -> int:
    """Calculates Hilbert curve order for a point in an n x n grid.

    Args:
        x: The x-coordinate.
        y: The y-coordinate.
        n: The grid size (must be a power of 2).

    Returns:
        The Hilbert curve order (distance along the curve).
    """
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
    """Adaptive exact cross product (orientation) with SOS tie-breaking.

    Args:
        a: The first point of the segment.
        b: The second point of the segment.
        p: The point to test.

    Returns:
        A positive value if p is to the left of ab, a negative value if p is to the right,
        and a non-zero tie-broken value if the points are collinear.
    """
    res = orient2d(a, b, p)
    if res != 0:
        return float(res)
        
    # Consistent tie-break using IDs
    return 1e-15 if (a.id < b.id) else -1e-15


def support(polygon: List[Point2D], direction: Point2D) -> Point2D:
    """Returns the point in the polygon that is furthest in the given direction.

    Args:
        polygon: A list of 2D points representing the polygon.
        direction: The direction vector (as a Point2D).

    Returns:
        The point in the polygon with the maximum projection onto the direction vector.
    """
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
