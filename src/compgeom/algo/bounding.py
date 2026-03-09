"""Minimum enclosing shapes for 2D point sets."""

from __future__ import annotations

import math
import random

from ..geo_math.geometry import EPSILON, Point
from ..geo_math.math_utils import rotate_2d, unrotate_2d
from ..polygon.polygon import graham_scan
from .proximity import welzl


def minimum_enclosing_circle(points):
    if not points:
        return Point(0, 0), 0.0
    shuffled = list(points)
    random.shuffle(shuffled)
    return welzl(shuffled, [])


def rectangle_corners(min_x, max_x, min_y, max_y, cos_theta, sin_theta):
    corners = [
        Point(min_x, min_y),
        Point(max_x, min_y),
        Point(max_x, max_y),
        Point(min_x, max_y),
    ]
    return [unrotate_2d(corner, cos_theta, sin_theta) for corner in corners]


def minimum_bounding_box(points):
    if not points:
        return {
            "area": 0.0,
            "width": 0.0,
            "height": 0.0,
            "angle": 0.0,
            "center": Point(0, 0),
            "corners": [],
        }

    if len(points) == 1:
        point = points[0]
        return {
            "area": 0.0,
            "width": 0.0,
            "height": 0.0,
            "angle": 0.0,
            "center": point,
            "corners": [point, point, point, point],
        }

    hull = graham_scan(list(points))
    if len(hull) == 2:
        a, b = hull
        dx = b.x - a.x
        dy = b.y - a.y
        angle = math.atan2(dy, dx)
        center = Point((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)
        return {
            "area": 0.0,
            "width": math.hypot(dx, dy),
            "height": 0.0,
            "angle": angle,
            "center": center,
            "corners": [a, b, b, a],
        }

    best = None
    for index, start in enumerate(hull):
        end = hull[(index + 1) % len(hull)]
        dx = end.x - start.x
        dy = end.y - start.y
        edge_length = math.hypot(dx, dy)
        if edge_length <= EPSILON:
            continue

        cos_theta = dx / edge_length
        sin_theta = dy / edge_length
        rotated = [rotate_2d(point, cos_theta, sin_theta) for point in hull]
        xs = [point.x for point in rotated]
        ys = [point.y for point in rotated]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x
        height = max_y - min_y
        area = width * height

        if best is None or area < best["area"]:
            center_rotated = Point((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)
            best = {
                "area": area,
                "width": width,
                "height": height,
                "angle": math.atan2(dy, dx),
                "center": unrotate_2d(center_rotated, cos_theta, sin_theta),
                "corners": rectangle_corners(min_x, max_x, min_y, max_y, cos_theta, sin_theta),
            }

    return best


__all__ = ["minimum_bounding_box", "minimum_enclosing_circle"]
