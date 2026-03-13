from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, List

if TYPE_CHECKING:
    from .point import Point2D

from .math_utils import (
    EPSILON, 
    cross_product,
)
from .triangle import area as triangle_area

def area(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> float:
    """Return the area of a quadrilateral (p1, p2, p3, p4)."""
    # Using the sum of two triangles (p1, p2, p3) and (p1, p3, p4)
    return abs(triangle_area(p1, p2, p3)) + abs(triangle_area(p1, p3, p4))


def is_convex(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> bool:
    """Check if quadrilateral (p1, p2, p3, p4) is convex."""
    # A quad is convex if all internal angles are < 180 degrees.
    # This is true if all cross products of consecutive edges have the same sign.
    cp1 = cross_product(p1, p2, p3)
    cp2 = cross_product(p2, p3, p4)
    cp3 = cross_product(p3, p4, p1)
    cp4 = cross_product(p4, p1, p2)
    
    return (
        (cp1 > EPSILON and cp2 > EPSILON and cp3 > EPSILON and cp4 > EPSILON) or
        (cp1 < -EPSILON and cp2 < -EPSILON and cp3 < -EPSILON and cp4 < -EPSILON)
    )


def split_to_triangles(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> list[tuple[Point2D, Point2D, Point2D]]:
    """Split a quadrilateral into two triangles."""
    # Standard split into two triangles
    return [(p1, p2, p3), (p1, p3, p4)]


def centroid(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Point2D:
    """Return the centroid of a quadrilateral."""
    from .point import Point2D
    return Point2D(
        (p1.x + p2.x + p3.x + p4.x) / 4.0,
        (p1.y + p2.y + p3.y + p4.y) / 4.0
    )


__all__ = [
    "area",
    "is_convex",
    "split_to_triangles",
    "centroid",
]
