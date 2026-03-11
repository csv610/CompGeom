"""Low-level geometry primitives and types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .math_utils import (
    EPSILON,
    cross_product,
    distance,
    dot_product,
    length,
    length_sq,
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


def clip_polygon(polygon: list[Point], line_start: Point, line_end: Point) -> list[Point]:
    """Clip a polygon against the left half-plane of the directed line."""
    from .line_segment import intersect_lines

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


__all__ = [
    "EPSILON",
    "Point",
    "Point3D",
    "clip_polygon",
    "cross_product",
    "dot_product",
    "length",
    "length_sq",
    "sub",
]
