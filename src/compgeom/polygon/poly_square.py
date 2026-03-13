"""Functions for squaring polygons by aligning segments to cardinal directions."""

from __future__ import annotations

import math
from ..kernel import Point2D
from .polygon_utils import rotate_polygon


def poly_square(polygon: list[Point2D], segment_index: int = 0) -> list[Point2D]:
    """
    Rotate the polygon such that the normal of the specified segment is aligned
    with its nearest cardinal direction (North, South, East, or West).
    
    This is equivalent to rotating the polygon so that the specified segment 
    becomes horizontal or vertical.
    """
    n = len(polygon)
    if n < 2:
        return polygon

    p1 = polygon[segment_index % n]
    p2 = polygon[(segment_index + 1) % n]

    # Angle of the segment (p1 -> p2)
    segment_angle = math.atan2(p2.y - p1.y, p2.x - p1.x)

    # To make the normal cardinal, the segment must be horizontal or vertical.
    # We want the segment angle to be a multiple of pi/2 (0, 90, 180, 270 degrees).
    target_angle = round(segment_angle / (math.pi / 2)) * (math.pi / 2)
    rotation_angle = target_angle - segment_angle

    return rotate_polygon(polygon, rotation_angle)


__all__ = ["poly_square"]
