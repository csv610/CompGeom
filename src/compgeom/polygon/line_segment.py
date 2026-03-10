"""Line segment helpers used by polygon algorithms."""

from __future__ import annotations

import math

from ..geo_math.geometry import EPSILON, Point, cross_product, is_on_segment, sub
from ..geo_math.math_utils import distance


def proper_segment_intersection(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1 = cross_product(a, b, c)
    o2 = cross_product(a, b, d)
    o3 = cross_product(c, d, a)
    o4 = cross_product(c, d, b)

    if abs(o1) <= EPSILON and is_on_segment(c, a, b):
        return False
    if abs(o2) <= EPSILON and is_on_segment(d, a, b):
        return False
    if abs(o3) <= EPSILON and is_on_segment(a, c, d):
        return False
    if abs(o4) <= EPSILON and is_on_segment(b, c, d):
        return False
    return (o1 > EPSILON) != (o2 > EPSILON) and (o3 > EPSILON) != (o4 > EPSILON)


def ray_segment_intersection(
    origin: Point, angle: float, start: Point, end: Point
) -> tuple[float, Point] | None:
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


__all__ = ["proper_segment_intersection", "ray_segment_intersection"]
