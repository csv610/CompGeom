"""Polygon algorithms and generators."""

from __future__ import annotations

import math
import random
from collections import deque

from .geometry import Point, contains_point, cross_product, is_on_segment, sub


class _TriangleView:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = (v1, v2, v3)


def _signed_area_twice(polygon: list[Point]) -> float:
    return sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


def _ensure_ccw(polygon: list[Point]) -> list[Point]:
    return polygon if _signed_area_twice(polygon) >= 0 else list(reversed(polygon))


def get_polygon_properties(polygon: list[Point]):
    area_twice = _signed_area_twice(polygon)
    area = area_twice / 2.0
    if abs(area) < 1e-12:
        return 0, Point(0, 0), "Degenerate"

    centroid_x = 0.0
    centroid_y = 0.0
    for index, p1 in enumerate(polygon):
        p2 = polygon[(index + 1) % len(polygon)]
        cross = (p1.x * p2.y) - (p2.x * p1.y)
        centroid_x += (p1.x + p2.x) * cross
        centroid_y += (p1.y + p2.y) * cross

    centroid_x /= 6.0 * area
    centroid_y /= 6.0 * area
    orientation = "CCW" if area > 0 else "CW"
    return abs(area), Point(centroid_x, centroid_y), orientation


def is_point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        if is_on_segment(point, start, end):
            return True

    inside = False
    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        intersects_scanline = (start.y > point.y) != (end.y > point.y)
        if intersects_scanline and point.x < (end.x - start.x) * (point.y - start.y) / (end.y - start.y) + start.x:
            inside = not inside
    return inside


def is_ear(a: Point, b: Point, c: Point, polygon: list[Point]) -> bool:
    if cross_product(a, b, c) <= 0:
        return False

    triangle = _TriangleView(a, b, c)
    return not any(
        point not in (a, b, c) and contains_point(triangle, point)
        for point in polygon
    )


def triangulate_polygon(polygon: list[Point]):
    polygon = _ensure_ccw(list(polygon))
    remaining_indices = list(range(len(polygon)))
    working_polygon = list(polygon)
    triangles: list[tuple[int, int, int]] = []

    while len(remaining_indices) > 3:
        for offset, current in enumerate(remaining_indices):
            prev_index = remaining_indices[offset - 1]
            next_index = remaining_indices[(offset + 1) % len(remaining_indices)]
            if is_ear(polygon[prev_index], polygon[current], polygon[next_index], working_polygon):
                triangles.append((prev_index, current, next_index))
                remaining_indices.pop(offset)
                working_polygon.pop(offset)
                break
        else:
            break

    if len(remaining_indices) == 3:
        triangles.append(tuple(remaining_indices))

    return triangles, polygon


def solve_art_gallery(polygon_input: list[Point]) -> list[Point]:
    triangles, polygon = triangulate_polygon(polygon_input)
    if not triangles:
        return []

    colors = {}
    first = triangles[0]
    colors[first[0]], colors[first[1]], colors[first[2]] = 0, 1, 2

    processed = [False] * len(triangles)
    processed[0] = True
    queue = deque([0])

    while queue:
        current_index = queue.popleft()
        current_triangle = triangles[current_index]
        for index, triangle in enumerate(triangles):
            if processed[index]:
                continue

            shared = set(current_triangle).intersection(triangle)
            if len(shared) != 2:
                continue

            new_vertex = next(iter(set(triangle) - shared))
            colors[new_vertex] = 3 - sum(colors[vertex] for vertex in shared)
            processed[index] = True
            queue.append(index)

    groups = [[], [], []]
    for vertex_index, color in colors.items():
        groups[color].append(polygon[vertex_index])
    return min(groups, key=len)


def get_triangulation_with_diagonals(polygon: list[Point]):
    polygon = _ensure_ccw(list(polygon))
    polygon_size = len(polygon)
    working_polygon = list(polygon)
    working_indices = list(range(polygon_size))
    triangles: list[tuple[int, int, int]] = []
    diagonals: list[tuple[int, int]] = []

    while len(working_indices) > 3:
        for offset, current in enumerate(working_indices):
            prev_index = working_indices[offset - 1]
            next_index = working_indices[(offset + 1) % len(working_indices)]
            if not is_ear(polygon[prev_index], polygon[current], polygon[next_index], working_polygon):
                continue

            triangles.append((prev_index, current, next_index))
            if abs(next_index - prev_index) != 1 and {prev_index, next_index} != {0, polygon_size - 1}:
                diagonals.append(tuple(sorted((prev_index, next_index))))
            working_indices.pop(offset)
            working_polygon.pop(offset)
            break
        else:
            break

    if len(working_indices) == 3:
        triangles.append(tuple(working_indices))
    return triangles, diagonals, polygon


def hertel_mehlhorn(polygon_input: list[Point]):
    triangles, diagonals, polygon = get_triangulation_with_diagonals(polygon_input)
    partitions = [list(triangle) for triangle in triangles]
    reflex_vertices = {
        index
        for index in range(len(polygon))
        if cross_product(polygon[index - 1], polygon[index], polygon[(index + 1) % len(polygon)]) <= 0
    }

    for diagonal in diagonals:
        shared_partitions = [
            partition_index
            for partition_index, partition in enumerate(partitions)
            if diagonal[0] in partition and diagonal[1] in partition
        ]
        if len(shared_partitions) != 2:
            continue

        u, v = diagonal
        if u in reflex_vertices or v in reflex_vertices:
            continue

        first, second = shared_partitions
        merged = list(set(partitions[first]) | set(partitions[second]))
        partitions.pop(max(first, second))
        partitions.pop(min(first, second))
        partitions.append(merged)

    return partitions, polygon


def graham_scan(points: list[Point]) -> list[Point]:
    if len(points) <= 2:
        return points

    anchor = min(points, key=lambda point: (point.y, point.x))

    def polar_order(point: Point):
        if point == anchor:
            return (-math.inf, 0)
        return (
            math.atan2(point.y - anchor.y, point.x - anchor.x),
            (point.x - anchor.x) ** 2 + (point.y - anchor.y) ** 2,
        )

    hull: list[Point] = []
    for point in sorted(points, key=polar_order):
        while len(hull) >= 2 and cross_product(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)
    return hull


def monotone_chain(points: list[Point]) -> list[Point]:
    if len(points) <= 2:
        return points

    ordered_points = sorted(points, key=lambda point: (point.x, point.y))
    lower: list[Point] = []
    for point in ordered_points:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper: list[Point] = []
    for point in reversed(ordered_points):
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def generate_random_convex_polygon(
    num_points: int = 10,
    x_range=(0, 100),
    y_range=(0, 100),
) -> list[Point]:
    points = [
        Point(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(num_points)
    ]
    return monotone_chain(points)


def is_convex(polygon: list[Point]) -> bool:
    if len(polygon) < 3:
        return True

    turn_directions = [
        cross_product(polygon[i], polygon[(i + 1) % len(polygon)], polygon[(i + 2) % len(polygon)])
        for i in range(len(polygon))
    ]
    non_zero_turns = [turn > 0 for turn in turn_directions if abs(turn) > 1e-9]
    return all(non_zero_turns) or not any(non_zero_turns)


def generate_simple_polygon(
    n_points: int = 20,
    x_range=(0, 100),
    y_range=(0, 100),
) -> list[Point]:
    points = [
        Point(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(n_points)
    ]
    center_x = sum(point.x for point in points) / n_points
    center_y = sum(point.y for point in points) / n_points
    ordered = sorted(points, key=lambda point: math.atan2(point.y - center_y, point.x - center_x))
    return [Point(point.x, point.y, index) for index, point in enumerate(ordered)]


def generate_points_in_triangle(a: Point, b: Point, c: Point, n_points: int = 100) -> list[Point]:
    edge_ab = sub(b, a)
    edge_ac = sub(c, a)
    samples: list[Point] = []
    for _ in range(n_points):
        r1 = random.random()
        r2 = random.random()
        if r1 + r2 > 1:
            r1, r2 = 1 - r1, 1 - r2
        samples.append(
            Point(
                a.x + r1 * edge_ab.x + r2 * edge_ac.x,
                a.y + r1 * edge_ab.y + r2 * edge_ac.y,
            )
        )
    return samples


__all__ = [
    "generate_points_in_triangle",
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "get_polygon_properties",
    "get_triangulation_with_diagonals",
    "graham_scan",
    "hertel_mehlhorn",
    "is_convex",
    "is_ear",
    "is_point_in_polygon",
    "monotone_chain",
    "solve_art_gallery",
    "triangulate_polygon",
]
