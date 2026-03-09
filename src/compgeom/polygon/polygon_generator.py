"""Polygon data structures and algorithms."""

from __future__ import annotations

import math
import random
from typing import List, Set, Tuple, Union

from ..geo_math.geometry import Point, cross_product
from ..geo_math.math_utils import distance
from .polygon import (
    generate_random_convex_polygon,
    generate_simple_polygon,
    get_triangulation_with_diagonals,
    _ensure_ccw,
)


class PolygonGenerator:
    """Provides methods for generating various types of polygons."""

    @staticmethod
    def convex(n_points: int = 10, x_range: Tuple[float, float] = (0, 100), y_range: Tuple[float, float] = (0, 100)) -> List[Point]:
        """Generates a random convex polygon with n_points."""
        return generate_random_convex_polygon(n_points, x_range, y_range)

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
