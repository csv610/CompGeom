"""Low-level geometry primitives and types."""

from __future__ import annotations

from typing import Optional

from .point import Point2D, Point3D
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

def clip_polygon(polygon: list[Point2D], line_start: Point2D, line_end: Point2D) -> list[Point2D]:
    """Clip a polygon against the left half-plane of the directed line."""
    from .line_segment import intersect_lines

    def is_inside(point: Point2D) -> bool:
        return cross_product(line_start, line_end, point) >= -1e-12

    clipped: list[Point2D] = []
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
    "Point2D",
    "Point3D",
    "clip_polygon",
    "cross_product",
    "dot_product",
    "length",
    "length_sq",
    "sub",
]
