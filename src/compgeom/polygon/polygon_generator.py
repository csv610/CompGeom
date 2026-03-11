"""Polygon data structures and algorithms."""

from __future__ import annotations

import math
import random
from typing import List, Tuple

from ..kernel import Point
from .convex_hull import ConvexHull
from .polygon import generate_simple_polygon


class PolygonGenerator:
    """Provides methods for generating various types of polygons."""

    @staticmethod
    def convex(n_points: int = 10, x_range: Tuple[float, float] = (0, 100), y_range: Tuple[float, float] = (0, 100)) -> List[Point]:
        """Generates a random convex polygon with n_points."""
        points = [
            Point(random.uniform(*x_range), random.uniform(*y_range), index)
            for index in range(n_points)
        ]
        return ConvexHull.monotone_chain(points)

    @staticmethod
    def concave(n_points: int = 15, x_range: Tuple[float, float] = (0, 100), y_range: Tuple[float, float] = (0, 100)) -> List[Point]:
        """
        Generates a random simple (potentially concave) polygon.
        Uses radial sorting with coordinate perturbation to ensure simplicity.
        """
        return generate_simple_polygon(n_points, x_range, y_range)

    @staticmethod
    def star_shaped(n_points: int = 15, center: Point = Point(50, 50), max_radius: float = 40.0) -> List[Point]:
        """Generates a random star-shaped polygon around a center point."""
        points = []
        for i in range(n_points):
            angle = 2.0 * math.pi * i / n_points
            # Randomly vary radius between 20% and 100% of max
            r = max_radius * (0.2 + 0.8 * random.random())
            points.append(Point(
                center.x + r * math.cos(angle),
                center.y + r * math.sin(angle),
                i
            ))
        return points


__all__ = ["PolygonGenerator"]
