"""Low-level geometry primitives and types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .math_utils import (
    EPSILON,
    cross_product,
    distance,
    dot_product,
    in_circle,
    incircle_det,
    incircle_sign,
    length,
    length_sq,
    orientation,
    orientation_sign,
    sub,
)


import math

@dataclass(frozen=True, eq=False, slots=True)
class Point:
    x: float
    y: float
    id: int = -1

    def __repr__(self) -> str:
        return f"P{self.id}({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Point)
            and math.isclose(self.x, other.x, abs_tol=EPSILON)
            and math.isclose(self.y, other.y, abs_tol=EPSILON)
        )

    def __hash__(self) -> int:
        return hash((round(self.x / EPSILON), round(self.y / EPSILON)))


@dataclass(frozen=True, eq=False, slots=True)
class Point3D:
    x: float
    y: float
    z: float
    id: int = -1

    def __repr__(self) -> str:
        return f"P{self.id}({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Point3D)
            and math.isclose(self.x, other.x, abs_tol=EPSILON)
            and math.isclose(self.y, other.y, abs_tol=EPSILON)
            and math.isclose(self.z, other.z, abs_tol=EPSILON)
        )

    def __hash__(self) -> int:
        return hash(
            (round(self.x / EPSILON), round(self.y / EPSILON), round(self.z / EPSILON))
        )


def get_circumcenter(a: Point, b: Point, c: Point) -> Optional[Point]:
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


def intersect_lines(p1: Point, p2: Point, p3: Point, p4: Point) -> Optional[Point]:
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
    return Point(px, py)


def clip_polygon(polygon: list[Point], line_start: Point, line_end: Point) -> list[Point]:
    """Clip a polygon against the left half-plane of the directed line."""

    def is_inside(point: Point) -> bool:
        return cross_product(line_start, line_end, point) >= -1e-12

    clipped: list[Point] = []
    n = len(polygon)
    if n == 0:
        return clipped

    for i in range(n):
        current = polygon[i]
        nxt = polygon[(i + 1) % n]
        current_inside = is_inside(current)
        next_inside = is_inside(nxt)

        if current_inside:
            if next_inside:
                clipped.append(nxt)
            else:
                intersection = intersect_lines(current, nxt, line_start, line_end)
                if intersection is not None:
                    clipped.append(intersection)
        else:
            if next_inside:
                intersection = intersect_lines(current, nxt, line_start, line_end)
                if intersection is not None:
                    clipped.append(intersection)
                clipped.append(nxt)
    return clipped


def dist_point_to_segment(point: Point, start: Point, end: Point) -> float:
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


def is_on_segment(point: Point, start: Point, end: Point) -> bool:
    if abs(cross_product(start, end, point)) > EPSILON:
        return False
    return (
        min(start.x, end.x) - EPSILON <= point.x <= max(start.x, end.x) + EPSILON
        and min(start.y, end.y) - EPSILON <= point.y <= max(start.y, end.y) + EPSILON
    )


def contains_point(triangle, point: Point) -> bool:
    a, b, c = triangle.vertices
    cp1 = orientation(a, b, point)
    cp2 = orientation(b, c, point)
    cp3 = orientation(c, a, point)
    return (
        cp1 >= -EPSILON and cp2 >= -EPSILON and cp3 >= -EPSILON
    ) or (
        cp1 <= EPSILON and cp2 <= EPSILON and cp3 <= EPSILON
    )


__all__ = [
    "EPSILON",
    "Point",
    "Point3D",
    "clip_polygon",
    "contains_point",
    "cross_product",
    "dist_point_to_segment",
    "dot_product",
    "get_circumcenter",
    "incircle_det",
    "incircle_sign",
    "in_circle",
    "intersect_lines",
    "is_on_segment",
    "length",
    "length_sq",
    "orientation",
    "orientation_sign",
    "sub",
]
