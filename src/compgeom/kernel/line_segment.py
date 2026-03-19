from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Tuple, Generic, TypeVar

from compgeom.kernel.point import Point2D, Point3D

from compgeom.kernel.math_utils import (
    EPSILON, 
    cross_product, 
    distance,
    sub,
    length,
    length_sq,
    dot_product
)

PointType = TypeVar('PointType', 'Point2D', 'Point3D')

@dataclass(frozen=True, slots=True)
class LineSegment(Generic[PointType]):
    """A line segment defined by start and end points.
    Can be embedded in 2D or 3D space depending on the PointType.
    """
    start: PointType
    end: PointType

    def length(self) -> float:
        return self.start.distance_to(self.end)

    def midpoint(self) -> PointType:
        return (self.start + self.end) * 0.5

    def direction(self) -> PointType:
        v = self.end - self.start
        d_len = v.length()
        if d_len < EPSILON:
            raise ValueError("Segment length is zero, direction undefined.")
        return v / d_len

    def distance_to_point(self, point: PointType) -> float:
        v = self.end - self.start
        w = point - self.start
        l2 = v.length_sq()
        if l2 < EPSILON:
            return self.start.distance_to(point)
        t = max(0.0, min(1.0, w.dot(v) / l2))
        projection = self.start + v * t
        return point.distance_to(projection)

    def __repr__(self) -> str:
        return f"LineSegment({self.start} -> {self.end})"


def intersect_lines(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Optional[Point2D]:
    """Return the line-line intersection, or ``None`` for parallel lines."""
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
    return Point2D(px, py)


def distance_to_point(point: Point2D, start: Point2D, end: Point2D) -> float:
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


def contains_point(point: Point2D, start: Point2D, end: Point2D) -> bool:
    """Check if a point lies on a line segment."""
    if abs(cross_product(start, end, point)) > EPSILON:
        return False
    return (
        min(start.x, end.x) - EPSILON <= point.x <= max(start.x, end.x) + EPSILON
        and min(start.y, end.y) - EPSILON <= point.y <= max(start.y, end.y) + EPSILON
    )


def intersect_proper(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
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
    origin: Point2D, angle: float, start: Point2D, end: Point2D
) -> tuple[float, Point2D] | None:
    """Return the intersection distance and point between a ray and a segment."""
    direction = Point2D(math.cos(angle), math.sin(angle))
    edge = sub(end, start)
    delta = sub(start, origin)
    denominator = direction.x * edge.y - direction.y * edge.x
    if abs(denominator) <= EPSILON:
        return None

    ray_t = (delta.x * edge.y - delta.y * edge.x) / denominator
    edge_u = (delta.x * direction.y - delta.y * direction.x) / denominator
    if ray_t < -EPSILON or edge_u < -EPSILON or edge_u > 1 + EPSILON:
        return None

    intersection = Point2D(origin.x + ray_t * direction.x, origin.y + ray_t * direction.y)
    if distance(intersection, start) <= 1e-6:
        intersection = start
    elif distance(intersection, end) <= 1e-6:
        intersection = end
    return ray_t, intersection


def midpoint(p1: Point2D, p2: Point2D) -> Point2D:
    """Return the midpoint of a line segment."""
    return Point2D((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)


def angle(p1: Point2D, p2: Point2D) -> float:
    """Return the angle of the segment (p1 -> p2) in radians."""
    return math.atan2(p2.y - p1.y, p2.x - p1.x)


__all__ = [
    "LineSegment",
    "intersect_lines",
    "distance_to_point",
    "contains_point",
    "intersect_proper",
    "intersect_ray",
    "midpoint",
    "angle",
]
