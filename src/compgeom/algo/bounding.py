"""Minimum enclosing shapes for 2D point sets."""

from __future__ import annotations

import math
import random

from compgeom.kernel import EPSILON, Point2D
from compgeom.kernel import rotate_2d, unrotate_2d
from compgeom.polygon.convex_hull import GrahamScan
from compgeom.algo.proximity import (
    welzl,
    find_largest_empty_circle,
    find_largest_empty_sphere,
    find_largest_empty_oriented_box,
    find_largest_empty_oriented_ellipsoid,
    find_largest_empty_oriented_rectangle,
    find_largest_empty_oriented_ellipse,
)


def largest_empty_circle(points):
    """Finds the largest empty circle whose center is within the convex hull."""
    return find_largest_empty_circle(list(points))


def minimum_enclosing_circle(points):
    if not points:
        return Point2D(0, 0), 0.0
    shuffled = list(points)
    random.shuffle(shuffled)
    return welzl(shuffled, [])


def rectangle_corners(min_x, max_x, min_y, max_y, cos_theta, sin_theta):
    corners = [
        Point2D(min_x, min_y),
        Point2D(max_x, min_y),
        Point2D(max_x, max_y),
        Point2D(min_x, max_y),
    ]
    return [unrotate_2d(corner, cos_theta, sin_theta) for corner in corners]


def minimum_bounding_box(points):
    if not points:
        return {
            "area": 0.0,
            "width": 0.0,
            "height": 0.0,
            "angle": 0.0,
            "center": Point2D(0, 0),
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

    hull = GrahamScan().generate(list(points))
    if len(hull) == 2:
        a, b = hull
        dx = b.x - a.x
        dy = b.y - a.y
        angle = math.atan2(dy, dx)
        center = Point2D((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)
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
            center_rotated = Point2D((min_x + max_x) / 2.0, (min_y + max_y) / 2.0)
            best = {
                "area": area,
                "width": width,
                "height": height,
                "angle": math.atan2(dy, dx),
                "center": unrotate_2d(center_rotated, cos_theta, sin_theta),
                "corners": rectangle_corners(min_x, max_x, min_y, max_y, cos_theta, sin_theta),
            }

    return best



def largest_empty_sphere(points):
    """Finds the largest empty sphere whose center is within the 3D convex hull."""
    return find_largest_empty_sphere(list(points))


def largest_empty_oriented_box(points):
    """Finds the largest empty oriented box within a 3D convex hull."""
    return find_largest_empty_oriented_box(list(points))


def largest_empty_oriented_ellipsoid(points):
    """Finds the largest empty oriented ellipsoid within a 3D convex hull."""
    return find_largest_empty_oriented_ellipsoid(list(points))


def largest_empty_oriented_rectangle(points):
    """Finds the largest empty oriented rectangle within a 2D convex hull."""
    return find_largest_empty_oriented_rectangle(list(points))


def largest_empty_oriented_ellipse(points):
    """Finds the largest empty oriented ellipse within a 2D convex hull."""
    return find_largest_empty_oriented_ellipse(list(points))

__all__ = ["largest_empty_oriented_ellipse", "largest_empty_oriented_rectangle", "largest_empty_oriented_ellipsoid", "largest_empty_oriented_box", "largest_empty_sphere", "largest_empty_circle", "minimum_bounding_box", "minimum_enclosing_circle"]
