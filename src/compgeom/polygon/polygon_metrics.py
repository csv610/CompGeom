"""Polygon metric and shape-query helpers."""

from __future__ import annotations

import math

from ..geo_math.geometry import Point, cross_product
from ..geo_math.math_utils import distance
from .polygon import Polygon, PolygonProperties


def get_polygon_properties(polygon: list[Point]) -> tuple[float, Point, str]:
    n = len(polygon)
    if n < 3:
        properties = PolygonProperties(0.0, Point(0, 0), "Degenerate")
        return properties.area, properties.centroid, properties.orientation

    area_twice = 0.0
    centroid_x = 0.0
    centroid_y = 0.0
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        cross = (p1.x * p2.y) - (p2.x * p1.y)
        area_twice += cross
        centroid_x += (p1.x + p2.x) * cross
        centroid_y += (p1.y + p2.y) * cross

    area = area_twice / 2.0
    if abs(area) < 1e-12:
        properties = PolygonProperties(0.0, Point(0, 0), "Degenerate")
        return properties.area, properties.centroid, properties.orientation

    centroid_x /= 6.0 * area
    centroid_y /= 6.0 * area
    orientation = "CCW" if area > 0 else "CW"
    return abs(area), Point(centroid_x, centroid_y), orientation


def is_convex(polygon: list[Point]) -> bool:
    if len(polygon) < 3:
        return True

    turn_directions = [
        cross_product(polygon[i], polygon[(i + 1) % len(polygon)], polygon[(i + 2) % len(polygon)])
        for i in range(len(polygon))
    ]
    non_zero_turns = [turn > 0 for turn in turn_directions if abs(turn) > 1e-9]
    return all(non_zero_turns) or not any(non_zero_turns)


def get_reflex_vertices(polygon: list[Point]) -> list[Point]:
    if len(polygon) < 3:
        return []

    poly = Polygon(polygon).ensure_ccw().as_list()
    reflex = []
    for i in range(len(poly)):
        p_prev = poly[i - 1]
        p_curr = poly[i]
        p_next = poly[(i + 1) % len(poly)]
        if cross_product(p_prev, p_curr, p_next) < -1e-9:
            reflex.append(p_curr)
    return reflex


def get_convex_diameter(polygon: list[Point]) -> float:
    if len(polygon) < 2:
        return 0.0
    if len(polygon) == 2:
        return distance(polygon[0], polygon[1])

    n = len(polygon)
    max_d_sq = 0.0
    k = 1

    for i in range(n):
        while True:
            area = abs(cross_product(polygon[i], polygon[(i + 1) % n], polygon[k]))
            next_area = abs(cross_product(polygon[i], polygon[(i + 1) % n], polygon[(k + 1) % n]))
            if next_area > area:
                k = (k + 1) % n
            else:
                break

        d1 = (polygon[i].x - polygon[k].x) ** 2 + (polygon[i].y - polygon[k].y) ** 2
        d2 = (polygon[(i + 1) % n].x - polygon[k].x) ** 2 + (polygon[(i + 1) % n].y - polygon[k].y) ** 2
        max_d_sq = max(max_d_sq, d1, d2)

    return math.sqrt(max_d_sq)


__all__ = ["get_convex_diameter", "get_polygon_properties", "get_reflex_vertices", "is_convex"]
