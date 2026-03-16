"""Functions for squaring polygons by aligning segments to cardinal directions."""

from __future__ import annotations

import math
from typing import Sequence

from ..kernel import Point2D
from .polygon import Polygon


def poly_square(polygon: Polygon | Sequence[Point2D], segment_index: int = 0) -> list[Point2D]:
    """
    Rotate the polygon such that the normal of the specified segment is aligned
    with its nearest cardinal direction (North, South, East, or West).
    """
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    vertices = poly_obj.vertices
    if segment_index < 0 or segment_index >= len(vertices):
        raise IndexError("Segment index out of range.")
    n = len(vertices)
    if n < 2:
        return list(vertices)

    p1 = vertices[segment_index % n]
    p2 = vertices[(segment_index + 1) % n]

    # Angle of the segment (p1 -> p2)
    segment_angle = math.atan2(p2.y - p1.y, p2.x - p1.x)

    # To make the normal cardinal, the segment must be horizontal or vertical.
    target_angle = round(segment_angle / (math.pi / 2)) * (math.pi / 2)
    rotation_angle = target_angle - segment_angle

    return poly_obj.rotate(rotation_angle).as_list()


__all__ = ["poly_square"]
