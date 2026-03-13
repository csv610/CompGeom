from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .point import Point

from .math_utils import (
    EPSILON, 
    cross_product, 
    distance,
    sub,
    length,
    length_sq,
    dot_product
)

def intersect_lines(p1: Point, p2: Point, p3: Point, p4: Point) -> Optional[Point]:
    """Return the line-line intersection, or ``None`` for parallel lines."""
    from .point import Point
    denominator = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if abs(denominator) < 1e-12:
        return None

    px = (
        (p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x)
        - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)
    ) / denominator
    py = (
        (p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y)
        - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)
    ) / denominator
    return Point(px, py)


def distance_to_point(point: Point, start: Point, end: Point) -> float:
    """Return the minimum distance from a point to a line segment."""
    dx = end.x - start.x
    dy = end.y - start.y
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(point.x - start.x, point.y - start.y)
    
    t = ((point.x - start.x) * dx + (point.y - start.y) * dy) / l2
    t = max(0, min(1, t))
    
    closest_x = start.x + t * dx
    closest_y = start.y + t * dy
    return math.hypot(point.x - closest_x, point.y - closest_y)


def contains_point(point: Point, start: Point, end: Point) -> bool:
    """Check if a point lies on a line segment."""
    if abs(cross_product(start, end, point)) > EPSILON:
        return False
    return (
        min(start.x, end.x) - EPSILON <= point.x <= max(start.x, end.x) + EPSILON
        and min(start.y, end.y) - EPSILON <= point.y <= max(start.y, end.y) + EPSILON
    )


def intersect_proper(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Check if segments AB and CD intersect properly (not at endpoints)."""
    o1 = cross_product(a, b, c)
    o2 = cross_product(a, b, d)
    o3 = cross_product(c, d, a)
    o4 = cross_product(c, d, b)

    if abs(o1) <= EPSILON and contains_point(c, a, b):
        return False
    if abs(o2) <= EPSILON and contains_point(d, a, b):
        return False
    if abs(o3) <= EPSILON and contains_point(a, c, d):
        return False
    if abs(o4) <= EPSILON and contains_point(b, c, d):
        return False
    return (o1 > EPSILON) != (o2 > EPSILON) and (o3 > EPSILON) != (o4 > EPSILON)


def intersect_ray(
    origin: Point, angle: float, start: Point, end: Point
) -> tuple[float, Point] | None:
    """Return the intersection distance and point between a ray and a segment."""
    from .point import Point
    direction = Point(math.cos(angle), math.sin(angle))
    edge = sub(end, start)
    delta = sub(start, origin)
    denominator = direction.x * edge.y - direction.y * edge.x
    if abs(denominator) <= EPSILON:
        return None

    ray_t = (delta.x * edge.y - delta.y * edge.x) / denominator
    edge_u = (delta.x * direction.y - delta.y * direction.x) / denominator
    if ray_t < -EPSILON or edge_u < -EPSILON or edge_u > 1 + EPSILON:
        return None

    intersection = Point(origin.x + ray_t * direction.x, origin.y + ray_t * direction.y)
    if distance(intersection, start) <= 1e-6:
        intersection = start
    elif distance(intersection, end) <= 1e-6:
        intersection = end
    return ray_t, intersection


def midpoint(p1: Point, p2: Point) -> Point:
    """Return the midpoint of a line segment."""
    from .point import Point
    return Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)


def angle(p1: Point, p2: Point) -> float:
    """Return the angle of the segment (p1 -> p2) in radians."""
    return math.atan2(p2.y - p1.y, p2.x - p1.x)


__all__ = [
    "intersect_lines",
    "distance_to_point",
    "contains_point",
    "intersect_proper",
    "intersect_ray",
    "midpoint",
    "angle",
]
