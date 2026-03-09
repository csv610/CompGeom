"""Distance, intersection, and enclosing-shape algorithms."""

from __future__ import annotations

import math

from .geometry import (
    Point,
    cross_product,
    dist_point_to_segment,
    dot_product,
    get_circumcenter,
    is_on_segment,
    length,
    sub,
)
from .math_utils import (
    distance,
    get_circle_three_points,
    get_circle_two_points,
    orientation as math_orientation,
    signed_area_twice,
    support,
)
from .polygon import graham_scan


def get_minkowski_support(poly1: list[Point], poly2: list[Point], direction: Point) -> Point:
    p1 = support(poly1, direction)
    p2 = support(poly2, Point(-direction.x, -direction.y))
    return sub(p1, p2)


def min_dist_convex_polygons(poly1: list[Point], poly2: list[Point]) -> float:
    direction = Point(1, 0)
    simplex = [get_minkowski_support(poly1, poly2, direction)]
    direction = Point(-simplex[0].x, -simplex[0].y)

    for _ in range(100):
        if length(direction) < 1e-9:
            return 0.0

        candidate = get_minkowski_support(poly1, poly2, direction)
        if dot_product(candidate, direction) < 0 and abs(dot_product(candidate, direction)) > 1e-9:
            return (
                length(simplex[0])
                if len(simplex) == 1
                else dist_point_to_segment(Point(0, 0), simplex[0], simplex[1])
            )

        simplex.append(candidate)
        if len(simplex) == 2:
            a, b = simplex[1], simplex[0]
            ab = sub(b, a)
            ao = Point(-a.x, -a.y)
            if dot_product(ab, ao) > 0:
                perpendicular = Point(-ab.y, ab.x)
                if dot_product(perpendicular, ao) < 0:
                    perpendicular = Point(ab.y, -ab.x)
                direction = perpendicular
            else:
                simplex = [a]
                direction = ao
            continue

        a, b, c = simplex[2], simplex[1], simplex[0]
        ab = sub(b, a)
        ac = sub(c, a)
        ao = Point(-a.x, -a.y)

        ab_perp = Point(-ab.y, ab.x)
        if dot_product(ab_perp, sub(c, a)) > 0:
            ab_perp = Point(ab.y, -ab.x)

        ac_perp = Point(-ac.y, ac.x)
        if dot_product(ac_perp, sub(b, a)) > 0:
            ac_perp = Point(ac.y, -ac.x)

        if dot_product(ab_perp, ao) > 0:
            simplex = [b, a]
            direction = ab_perp
        elif dot_product(ac_perp, ao) > 0:
            simplex = [c, a]
            direction = ac_perp
        else:
            return 0.0

    return 0.0


def closest_pair(points: list[Point]):
    if len(points) <= 3:
        min_distance = float("inf")
        pair = (None, None)
        for left in range(len(points)):
            for right in range(left + 1, len(points)):
                d = distance(points[left], points[right])
                if d < min_distance:
                    min_distance = d
                    pair = (points[left], points[right])
        return min_distance, pair

    ordered = sorted(points, key=lambda point: point.x)
    midpoint = len(ordered) // 2
    left_distance, left_pair = closest_pair(ordered[:midpoint])
    right_distance, right_pair = closest_pair(ordered[midpoint:])
    best_distance, best_pair = (
        (left_distance, left_pair) if left_distance < right_distance else (right_distance, right_pair)
    )

    strip = sorted(
        [point for point in ordered if abs(point.x - ordered[midpoint].x) < best_distance],
        key=lambda point: point.y,
    )
    for left in range(len(strip)):
        for right in range(left + 1, len(strip)):
            if strip[right].y - strip[left].y >= best_distance:
                break
            d = distance(strip[left], strip[right])
            if d < best_distance:
                best_distance = d
                best_pair = (strip[left], strip[right])

    return best_distance, best_pair


def do_intersect(p1: Point, q1: Point, p2: Point, q2: Point) -> bool:
    o1 = math_orientation(p1, q1, p2)
    o2 = math_orientation(p1, q1, q2)
    o3 = math_orientation(p2, q2, p1)
    o4 = math_orientation(p2, q2, q1)

    # Note: math_orientation returns float, we check signs
    # but the logic in original was returning 0, 1, 2. 
    # Let's use the cross_product sign logic here for simplicity.
    
    def get_sign(val):
        if abs(val) < 1e-9: return 0
        return 1 if val > 0 else 2

    s1, s2, s3, s4 = get_sign(o1), get_sign(o2), get_sign(o3), get_sign(o4)

    return (
        (s1 != s2 and s3 != s4)
        or (s1 == 0 and is_on_segment(p2, p1, q1))
        or (s2 == 0 and is_on_segment(q2, p1, q1))
        or (s3 == 0 and is_on_segment(p1, p2, q2))
        or (s4 == 0 and is_on_segment(q1, p2, q2))
    )


def farthest_pair(points: list[Point]):
    hull = graham_scan(points)
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
            current_area = abs(cross_product(hull[index], hull[(index + 1) % len(hull)], hull[k]))
            next_area = abs(cross_product(hull[index], hull[(index + 1) % len(hull)], hull[(k + 1) % len(hull)]))
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


def welzl(points: list[Point], boundary: list[Point]):
    if not points or len(boundary) == 3:
        if not boundary:
            return Point(0, 0), 0
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


def minkowski_sum(poly1: list[Point], poly2: list[Point]) -> list[Point]:
    if not poly1 or not poly2:
        return []

    def prepare_polygon(polygon: list[Point]) -> list[Point]:
        area_twice = signed_area_twice(polygon)
        ordered = polygon if area_twice >= 0 else list(reversed(polygon))
        start_index = min(range(len(ordered)), key=lambda index: (ordered[index].y, ordered[index].x))
        return ordered[start_index:] + ordered[:start_index]

    p1 = prepare_polygon(poly1)
    p2 = prepare_polygon(poly2)
    p1.append(p1[0])
    p2.append(p2[0])

    result: list[Point] = []
    i = j = 0
    n = len(p1) - 1
    m = len(p2) - 1
    while i < n or j < m:
        result.append(Point(p1[i % n].x + p2[j % m].x, p1[i % n].y + p2[j % m].y))
        if i < n and j < m:
            angle1 = math.atan2(p1[i + 1].y - p1[i].y, p1[i + 1].x - p1[i].x) % (2 * math.pi)
            angle2 = math.atan2(p2[j + 1].y - p2[j].y, p2[j + 1].x - p2[j].x) % (2 * math.pi)
            if angle1 < angle2:
                i += 1
            elif angle1 > angle2:
                j += 1
            else:
                i += 1
                j += 1
        elif i < n:
            i += 1
        else:
            j += 1
    return result


__all__ = [
    "closest_pair",
    "do_intersect",
    "farthest_pair",
    "get_circle_three_points",
    "get_circle_two_points",
    "get_minkowski_support",
    "min_dist_convex_polygons",
    "minkowski_sum",
    "support",
    "welzl",
]
