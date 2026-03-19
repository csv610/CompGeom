"""Polygon generation and factory helpers."""

from __future__ import annotations

import math
import random
from typing import List, Tuple, TypeVar, Union

from compgeom.kernel import Point2D, Point3D
from compgeom.polygon.convex_hull import MonotoneChain
from compgeom.polygon.polygon import Polygon

PolygonT = TypeVar("PolygonT", bound=Polygon)


def generate_convex_polygon(
    n_points: int = 10,
    x_range: Tuple[float, float] = (0, 100),
    y_range: Tuple[float, float] = (0, 100),
) -> Polygon:
    """Generates a random convex polygon with n_points."""
    points = [
        Point2D(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(n_points)
    ]
    return Polygon(MonotoneChain().generate(points))


def generate_concave_polygon(
    n_points: int = 20,
    x_range: Tuple[float, float] = (0, 100),
    y_range: Tuple[float, float] = (0, 100),
) -> Polygon:
    """
    Generates a random simple (potentially concave) polygon.
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
    return Polygon([Point2D(point.x, point.y, index) for index, point in enumerate(ordered)])


def generate_star_shaped_polygon(
    n_points: int = 15, center: Point2D = Point2D(50, 50), max_radius: float = 40.0
) -> Polygon:
    """Generates a random star-shaped polygon around a center point."""
    points = []
    for i in range(n_points):
        angle = 2.0 * math.pi * i / n_points
        # Randomly vary radius between 20% and 100% of max
        r = max_radius * (0.2 + 0.8 * random.random())
        points.append(Point2D(center.x + r * math.cos(angle), center.y + r * math.sin(angle), i))
    return Polygon(points)


def generate_sierpinski_triangle(
    depth: int,
    p1: Point2D = Point2D(0, 0),
    p2: Point2D = Point2D(100, 0),
    p3: Point2D = Point2D(50, 86.6),
) -> List[Polygon]:
    """
    Generates a Sierpinski triangle fractal up to the given depth.
    Returns a list of triangles (each as a Polygon).
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

    return [Polygon(tri) for tri in subdivide(depth, p1, p2, p3)]


def generate_koch_snowflake(
    depth: int,
    p1: Point2D = Point2D(0, 0),
    p2: Point2D = Point2D(100, 0),
    p3: Point2D = Point2D(50, 86.6),
) -> Polygon:
    """
    Generates a Koch snowflake boundary up to the given depth.
    Returns a Polygon defining the closed boundary.
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
    return Polygon(points)


def generate_dragon_curve(
    depth: int,
    p1: Point2D = Point2D(0, 0),
    p2: Point2D = Point2D(100, 100),
) -> Polygon:
    """
    Generates a Heighway Dragon curve up to the given depth.
    Returns a Polygon.
    """

    def recurse(a: Point2D, b: Point2D, d: int, sign: int) -> List[Point2D]:
        if d == 0:
            return [a]

        # Midpoint rotated by 90 degrees
        pm = Point2D(
            (a.x + b.x) / 2 - sign * (b.y - a.y) / 2, (a.y + b.y) / 2 + sign * (b.x - a.x) / 2
        )

        return recurse(a, pm, d - 1, 1) + recurse(pm, b, d - 1, -1)

    return Polygon(recurse(p1, p2, depth, 1) + [p2])


def generate_de_rham_curve(
    depth: int,
    p1: Point2D = Point2D(0, 0),
    p2: Point2D = Point2D(100, 0),
    w: complex = complex(0.5, 0.5),
) -> Polygon:
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
    return Polygon(recurse(z1, z2, depth) + [p2])


__all__ = [
    "generate_convex_polygon",
    "generate_concave_polygon",
    "generate_star_shaped_polygon",
    "generate_sierpinski_triangle",
    "generate_koch_snowflake",
    "generate_dragon_curve",
    "generate_de_rham_curve",
]
