"""Convex hull construction algorithms."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from compgeom.kernel import EPSILON, Point2D, Point3D, cross_product
from compgeom.kernel import distance


class ConvexHull:
    """Unified interface for generating convex hulls in 2D and 3D."""

    @staticmethod
    def generate(points: list[Point2D] | list[Point3D], algorithm: str = "scipy"):
        """
        Generate the convex hull for a set of points.

        Args:
            points: A list of Point2D or Point3D objects.
            algorithm: The algorithm to use for 2D points ("scipy", "graham_scan", "monotone_chain", "quickhull", "chan").
                       Defaults to "scipy".
                       For 3D points, a TriMesh is returned using SciPy's Qhull.

        Returns:
            A list of Point2D representing the hull boundary for 2D points,
            or a TriMesh for 3D points.
        """
        if not points:
            return []

        p0 = points[0]
        if isinstance(p0, Point2D):
            alg_map = {
                "scipy": ScipyConvexHull2D,
                "graham_scan": GrahamScan,
                "monotone_chain": MonotoneChain,
                "quickhull": QuickHull,
                "chan": Chan,
            }
            # Fallback to ScipyConvexHull2D (which itself falls back to MonotoneChain if scipy is missing)
            # if algorithm name is invalid.
            generator_cls = alg_map.get(algorithm.lower().replace(" ", "_"), ScipyConvexHull2D)
            return generator_cls().generate(points)

        if isinstance(p0, Point3D):
            from compgeom.mesh.surface.convex_hull import ConvexHull3D
            return ConvexHull3D.compute(points)

        raise TypeError("Points must be a list of Point2D or Point3D objects.")


class ConvexHullGenerator(ABC):
    """Abstract base class for convex hull algorithms."""

    @abstractmethod
    def generate(self, points: list[Point2D]) -> list[Point2D]:
        """Generate the convex hull for a set of points."""
        pass

    @staticmethod
    def is_convex_hull(points: list[Point2D], hull: list[Point2D]) -> bool:
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

        from compgeom.polygon.polygon import Polygon

        hull_polygon = Polygon(hull)
        for point in unique_points:
            if not hull_polygon.contains_point(point):
                return False
        return True


class ScipyConvexHull2D(ConvexHullGenerator):
    """2D Convex Hull using SciPy's Qhull implementation."""
    def generate(self, points: list[Point2D]) -> list[Point2D]:
        if len(points) <= 2:
            return points

        try:
            import numpy as np
            from scipy.spatial import ConvexHull as ScipyHull
            
            pts_array = np.array([[p.x, p.y] for p in points])
            hull = ScipyHull(pts_array)
            return [points[idx] for idx in hull.vertices]
        except ImportError:
            # Fallback to MonotoneChain if scipy/numpy is not available
            return MonotoneChain().generate(points)


class GrahamScan(ConvexHullGenerator):
    def generate(self, points: list[Point2D]) -> list[Point2D]:
        if len(points) <= 2:
            return points

        anchor = min(points, key=lambda point: (point.y, point.x))

        def polar_order(point: Point2D):
            if point == anchor:
                return (-math.inf, 0)
            return (
                math.atan2(point.y - anchor.y, point.x - anchor.x),
                (point.x - anchor.x) ** 2 + (point.y - anchor.y) ** 2,
            )

        hull: list[Point2D] = []
        for point in sorted(points, key=polar_order):
            while len(hull) >= 2 and cross_product(hull[-2], hull[-1], point) <= 0:
                hull.pop()
            hull.append(point)
        return hull


class MonotoneChain(ConvexHullGenerator):
    def generate(self, points: list[Point2D]) -> list[Point2D]:
        if len(points) <= 2:
            return points

        ordered_points = sorted(points, key=lambda point: (point.x, point.y))
        lower: list[Point2D] = []
        for point in ordered_points:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], point) <= 0:
                lower.pop()
            lower.append(point)

        upper: list[Point2D] = []
        for point in reversed(ordered_points):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], point) <= 0:
                upper.pop()
            upper.append(point)

        return lower[:-1] + upper[:-1]


class QuickHull(ConvexHullGenerator):
    def generate(self, points: list[Point2D]) -> list[Point2D]:
        if len(points) <= 2:
            return points

        unique_points = sorted(set(points), key=lambda point: (point.x, point.y))
        if len(unique_points) <= 2:
            return unique_points

        leftmost = unique_points[0]
        rightmost = unique_points[-1]

        def distance_from_line(a: Point2D, b: Point2D, p: Point2D) -> float:
            return abs(cross_product(a, b, p))

        def build_hull(a: Point2D, b: Point2D, candidates: list[Point2D]) -> list[Point2D]:
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
        return MonotoneChain().generate(hull)


class Chan(ConvexHullGenerator):
    def generate(self, points: list[Point2D]) -> list[Point2D]:
        unique_points = sorted(set(points), key=lambda point: (point.x, point.y))
        if len(unique_points) <= 2:
            return unique_points

        n = len(unique_points)
        t = 1
        while True:
            m = min(1 << (1 << t), n)
            hulls = [
                MonotoneChain().generate(unique_points[i : i + m]) for i in range(0, n, m)
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
                        next_point = self._next_hull_point(hull[-1], next_point, point)

                if next_point is None:
                    return hull
                if next_point == start:
                    return MonotoneChain().generate(hull)
                hull.append(next_point)

            t += 1

    def _next_hull_point(self, current: Point2D, candidate: Point2D, challenger: Point2D) -> Point2D:
        turn = cross_product(current, candidate, challenger)
        if turn < -EPSILON:
            return challenger
        if abs(turn) <= EPSILON and distance(current, challenger) > distance(current, candidate):
            return challenger
        return candidate


__all__ = [
    "ConvexHull",
    "ConvexHullGenerator",
    "GrahamScan",
    "MonotoneChain",
    "QuickHull",
    "Chan",
]