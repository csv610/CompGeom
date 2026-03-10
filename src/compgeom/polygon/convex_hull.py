"""Convex hull construction algorithms."""

from __future__ import annotations

import math

from ..geo_math.geometry import EPSILON, Point, cross_product
from ..geo_math.math_utils import distance


class ConvexHull:
    """Convex hull construction algorithms."""

    @staticmethod
    def _next_hull_point(current: Point, candidate: Point, challenger: Point) -> Point:
        turn = cross_product(current, candidate, challenger)
        if turn < -EPSILON:
            return challenger
        if abs(turn) <= EPSILON and distance(current, challenger) > distance(current, candidate):
            return challenger
        return candidate

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def quick_hull(points: list[Point]) -> list[Point]:
        if len(points) <= 2:
            return points

        unique_points = sorted(set(points), key=lambda point: (point.x, point.y))
        if len(unique_points) <= 2:
            return unique_points

        leftmost = unique_points[0]
        rightmost = unique_points[-1]

        def distance_from_line(a: Point, b: Point, p: Point) -> float:
            return abs(cross_product(a, b, p))

        def build_hull(a: Point, b: Point, candidates: list[Point]) -> list[Point]:
            if not candidates:
                return []

            farthest = max(candidates, key=lambda point: distance_from_line(a, b, point))
            left_of_af = [point for point in candidates if cross_product(a, farthest, point) > EPSILON]
            left_of_fb = [point for point in candidates if cross_product(farthest, b, point) > EPSILON]
            return build_hull(a, farthest, left_of_af) + [farthest] + build_hull(farthest, b, left_of_fb)

        upper = [point for point in unique_points[1:-1] if cross_product(leftmost, rightmost, point) > EPSILON]
        lower = [point for point in unique_points[1:-1] if cross_product(rightmost, leftmost, point) > EPSILON]

        hull = [leftmost] + build_hull(leftmost, rightmost, upper) + [rightmost] + build_hull(
            rightmost,
            leftmost,
            lower,
        )
        return ConvexHull.monotone_chain(hull)

    @staticmethod
    def chan(points: list[Point]) -> list[Point]:
        unique_points = sorted(set(points), key=lambda point: (point.x, point.y))
        if len(unique_points) <= 2:
            return unique_points

        n = len(unique_points)
        t = 1
        while True:
            m = min(1 << (1 << t), n)
            hulls = [
                ConvexHull.monotone_chain(unique_points[i : i + m]) for i in range(0, n, m)
            ]
            start = min(unique_points, key=lambda point: (point.x, point.y))
            hull = [start]

            for _ in range(m):
                next_point = None
                for sub_hull in hulls:
                    for point in sub_hull:
                        if point == hull[-1]:
                            continue
                        if next_point is None:
                            next_point = point
                            continue
                        next_point = ConvexHull._next_hull_point(hull[-1], next_point, point)

                if next_point is None:
                    return hull
                if next_point == start:
                    return ConvexHull.monotone_chain(hull)
                hull.append(next_point)

            t += 1

    @staticmethod
    def is_convex_hull(points: list[Point], hull: list[Point]) -> bool:
        if not hull:
            return len(set(points)) == 0

        unique_points = set(points)
        if any(vertex not in unique_points for vertex in hull):
            return False
        if len(set(hull)) != len(hull):
            return False
        if len(hull) == 1:
            return len(unique_points) == 1 and hull[0] in unique_points
        if len(hull) == 2:
            a, b = hull
            return all(abs(cross_product(a, b, point)) <= EPSILON for point in unique_points)

        for i in range(len(hull)):
            if cross_product(hull[i - 1], hull[i], hull[(i + 1) % len(hull)]) <= EPSILON:
                return False

        from .polygon import Polygon

        hull_polygon = Polygon(hull)
        for point in unique_points:
            if not hull_polygon.contains_point(point):
                return False
        return True


def graham_scan(points: list[Point]) -> list[Point]:
    return ConvexHull.graham_scan(points)


def monotone_chain(points: list[Point]) -> list[Point]:
    return ConvexHull.monotone_chain(points)


__all__ = ["ConvexHull", "graham_scan", "monotone_chain"]
