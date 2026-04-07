from __future__ import annotations

import math
from typing import List, Tuple, Optional

from compgeom.kernel import (
    Point2D,
    cross_product,
    distance,
    get_circle_three_points,
    get_circle_two_points,
    is_on_segment,
    orientation as math_orientation,
    support,
)
from compgeom.polygon.convex_hull import GrahamScan

__all__ = [
    "do_intersect",
    "farthest_pair",
    "welzl",
    "get_circle_three_points",
    "get_circle_two_points",
    "support",
]


def do_intersect(p1: Point2D, q1: Point2D, p2: Point2D, q2: Point2D) -> bool:
    o1 = math_orientation(p1, q1, p2)
    o2 = math_orientation(p1, q1, q2)
    o3 = math_orientation(p2, q2, p1)
    o4 = math_orientation(p2, q2, q1)

    def get_sign(val):
        if abs(val) < 1e-9:
            return 0
        return 1 if val > 0 else 2

    s1, s2, s3, s4 = get_sign(o1), get_sign(o2), get_sign(o3), get_sign(o4)

    return (
        (s1 != s2 and s3 != s4)
        or (s1 == 0 and is_on_segment(p2, p1, q1))
        or (s2 == 0 and is_on_segment(q2, p1, q1))
        or (s3 == 0 and is_on_segment(p1, p2, q2))
        or (s4 == 0 and is_on_segment(q1, p2, q2))
    )


def farthest_pair(points: List[Point2D]) -> Tuple[float, Tuple[Optional[Point2D], Optional[Point2D]]]:
    hull = GrahamScan().generate(points)
    if len(hull) == 0:
        return 0, (None, None)
    if len(hull) == 1:
        return 0, (hull[0], hull[0])
    if len(hull) == 2:
        return distance(hull[0], hull[1]), (hull[0], hull[1])

    max_distance = 0.0
    pair = (None, None)
    k = 1
    for index in range(len(hull)):
        while True:
            current_area = abs(
                cross_product(hull[index], hull[(index + 1) % len(hull)], hull[k])
            )
            next_area = abs(
                cross_product(
                    hull[index],
                    hull[(index + 1) % len(hull)],
                    hull[(k + 1) % len(hull)],
                )
            )
            if next_area > current_area:
                k = (k + 1) % len(hull)
            else:
                break

        d1 = distance(hull[index], hull[k])
        d2 = distance(hull[(index + 1) % len(hull)], hull[k])
        if d1 > max_distance:
            max_distance = d1
            pair = (hull[index], hull[k])
        if d2 > max_distance:
            max_distance = d2
            pair = (hull[(index + 1) % len(hull)], hull[k])

    return max_distance, pair


def welzl(points: List[Point2D], boundary: List[Point2D]) -> Tuple[Point2D, float]:
    if not points or len(boundary) == 3:
        if not boundary:
            return Point2D(0, 0), 0
        if len(boundary) == 1:
            return boundary[0], 0
        if len(boundary) == 2:
            return get_circle_two_points(boundary[0], boundary[1])
        return get_circle_three_points(boundary[0], boundary[1], boundary[2])

    point = points.pop()
    center, radius = welzl(points, boundary)
    if distance(center, point) <= radius + 1e-9:
        points.append(point)
        return center, radius

    boundary.append(point)
    result = welzl(points, boundary)
    boundary.pop()
    points.append(point)
    return result
