"""Polygon generation and factory helpers."""

from __future__ import annotations

import math
import random
from typing import List, Tuple, TypeVar

from ..kernel import Point2D
from .convex_hull import MonotoneChain
from .polygon import Polygon

PolygonT = TypeVar("PolygonT", bound=Polygon)


class PolygonGenerator:
    """Provides methods for generating various types of polygons."""

    @staticmethod
    def convex(
        n_points: int = 10,
        x_range: Tuple[float, float] = (0, 100),
        y_range: Tuple[float, float] = (0, 100),
    ) -> List[Point2D]:
        """Generates points for a random convex polygon with n_points."""
        points = [
            Point2D(random.uniform(*x_range), random.uniform(*y_range), index)
            for index in range(n_points)
        ]
        return MonotoneChain().generate(points)

    @staticmethod
    def concave(
        n_points: int = 20,
        x_range: Tuple[float, float] = (0, 100),
        y_range: Tuple[float, float] = (0, 100),
    ) -> List[Point2D]:
        """
        Generates points for a random simple (potentially concave) polygon.
        Uses radial sorting with coordinate perturbation to ensure simplicity.
        """
        points = [
            Point2D(random.uniform(*x_range), random.uniform(*y_range), index)
            for index in range(n_points)
        ]
        center_x = sum(point.x for point in points) / n_points
        center_y = sum(point.y for point in points) / n_points
        ordered = sorted(
            points, key=lambda point: math.atan2(point.y - center_y, point.x - center_x)
        )
        return [Point2D(point.x, point.y, index) for index, point in enumerate(ordered)]

    @staticmethod
    def star_shaped(
        n_points: int = 15, center: Point2D = Point2D(50, 50), max_radius: float = 40.0
    ) -> List[Point2D]:
        """Generates a random star-shaped polygon around a center point."""
        points = []
        for i in range(n_points):
            angle = 2.0 * math.pi * i / n_points
            # Randomly vary radius between 20% and 100% of max
            r = max_radius * (0.2 + 0.8 * random.random())
            points.append(Point2D(center.x + r * math.cos(angle), center.y + r * math.sin(angle), i))
        return points

    @staticmethod
    def sierpinski_triangle(
        depth: int,
        p1: Point2D = Point2D(0, 0),
        p2: Point2D = Point2D(100, 0),
        p3: Point2D = Point2D(50, 86.6),
    ) -> List[List[Point2D]]:
        """
        Generates a Sierpinski triangle fractal up to the given depth.
        Returns a list of triangles (each as a list of 3 Points).
        """

        def get_midpoint(a: Point2D, b: Point2D) -> Point2D:
            return Point2D((a.x + b.x) / 2, (a.y + b.y) / 2)

        def subdivide(d: int, a: Point2D, b: Point2D, c: Point2D) -> List[List[Point2D]]:
            if d == 0:
                return [[a, b, c]]

            m12 = get_midpoint(a, b)
            m23 = get_midpoint(b, c)
            m31 = get_midpoint(c, a)

            triangles = []
            triangles.extend(subdivide(d - 1, a, m12, m31))
            triangles.extend(subdivide(d - 1, m12, b, m23))
            triangles.extend(subdivide(d - 1, m31, m23, c))
            return triangles

        return subdivide(depth, p1, p2, p3)

    @staticmethod
    def koch_snowflake(
        depth: int,
        p1: Point2D = Point2D(0, 0),
        p2: Point2D = Point2D(100, 0),
        p3: Point2D = Point2D(50, 86.6),
    ) -> List[Point2D]:
        """
        Generates a Koch snowflake boundary up to the given depth.
        Returns a list of Points defining the closed boundary.
        """

        def koch_curve(a: Point2D, b: Point2D, d: int) -> List[Point2D]:
            if d == 0:
                return [a]

            dx, dy = b.x - a.x, b.y - a.y
            m1 = Point2D(a.x + dx / 3, a.y + dy / 3)
            m2 = Point2D(a.x + 2 * dx / 3, a.y + 2 * dy / 3)

            # Peak of the triangle (60 degrees)
            s32 = math.sqrt(3) / 6
            peak = Point2D((a.x + b.x) / 2 - dy * s32, (a.y + b.y) / 2 + dx * s32)

            return (
                koch_curve(a, m1, d - 1)
                + koch_curve(m1, peak, d - 1)
                + koch_curve(peak, m2, d - 1)
                + koch_curve(m2, b, d - 1)
            )

        points = []
        points.extend(koch_curve(p1, p2, depth))
        points.extend(koch_curve(p2, p3, depth))
        points.extend(koch_curve(p3, p1, depth))
        return points

    @staticmethod
    def dragon_curve(
        depth: int,
        p1: Point2D = Point2D(0, 0),
        p2: Point2D = Point2D(100, 100),
    ) -> List[Point2D]:
        """
        Generates a Heighway Dragon curve up to the given depth.
        Returns a list of Points.
        """

        def recurse(a: Point2D, b: Point2D, d: int, sign: int) -> List[Point2D]:
            if d == 0:
                return [a]

            # Midpoint rotated by 90 degrees
            pm = Point2D(
                (a.x + b.x) / 2 - sign * (b.y - a.y) / 2, (a.y + b.y) / 2 + sign * (b.x - a.x) / 2
            )

            return recurse(a, pm, d - 1, 1) + recurse(pm, b, d - 1, -1)

        return recurse(p1, p2, depth, 1) + [p2]

    @staticmethod
    def de_rham_curve(
        depth: int,
        p1: Point2D = Point2D(0, 0),
        p2: Point2D = Point2D(100, 0),
        w: complex = complex(0.5, 0.5),
    ) -> List[Point2D]:
        """
        Generates a De Rham curve (e.g., Lévy C curve) up to the given depth.
        w is the complex parameter defining the transformation.
        """

        def recurse(z1: complex, z2: complex, d: int) -> List[Point2D]:
            if d == 0:
                return [Point2D(z1.real, z1.imag)]

            # Iterative mapping z -> f_i(z)
            zm = z1 + w * (z2 - z1)

            return recurse(z1, zm, d - 1) + recurse(zm, z2, d - 1)

        z1 = complex(p1.x, p1.y)
        z2 = complex(p2.x, p2.y)
        return recurse(z1, z2, depth) + [p2]


def random_convex_points(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point2D]:
    return PolygonGenerator.convex(num_points, x_range, y_range)


def simple_polygon_points(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point2D]:
    return PolygonGenerator.concave(n_points, x_range, y_range)


def random_convex_polygon(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
    *,
    polygon_cls: type[PolygonT] = Polygon,
) -> PolygonT:
    return polygon_cls(random_convex_points(num_points, x_range, y_range))


def simple_polygon(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
    *,
    polygon_cls: type[PolygonT] = Polygon,
) -> PolygonT:
    return polygon_cls(simple_polygon_points(n_points, x_range, y_range))


def generate_random_convex_polygon(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point2D]:
    return random_convex_polygon(num_points, x_range, y_range).as_list()


def generate_simple_polygon(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point2D]:
    return simple_polygon(n_points, x_range, y_range).as_list()


__all__ = [
    "PolygonGenerator",
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "random_convex_polygon",
    "random_convex_points",
    "simple_polygon",
    "simple_polygon_points",
]
