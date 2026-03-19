"""Sampling helpers for geometric domains."""

from __future__ import annotations

import math
import random
from typing import List, Optional

from compgeom.kernel import Point2D, Point3D


class PointSampler:
    """Class for sampling points from different geometric domains."""

    @staticmethod
    def in_circle(center: Point2D, radius: float, n_points: int = 100) -> List[Point2D]:
        """Samples points uniformly from the interior of a circle."""
        points = []
        for index in range(n_points):
            angle = random.uniform(0.0, 2.0 * math.pi)
            distance = radius * math.sqrt(random.random())
            points.append(
                Point2D(
                    center.x + distance * math.cos(angle),
                    center.y + distance * math.sin(angle),
                    index,
                )
            )
        return points

    @staticmethod
    def on_circle(center: Point2D, radius: float, n_points: int = 100) -> List[Point2D]:
        """Samples points uniformly from the boundary of a circle."""
        points = []
        for index in range(n_points):
            angle = random.uniform(0.0, 2.0 * math.pi)
            points.append(
                Point2D(
                    center.x + radius * math.cos(angle),
                    center.y + radius * math.sin(angle),
                    index,
                )
            )
        return points

    @staticmethod
    def in_rectangle(
        width: float, height: float, n_points: int = 100, center: Optional[Point2D] = None
    ) -> List[Point2D]:
        """Samples points uniformly from the interior of a rectangle."""
        center = center or Point2D(0.0, 0.0)
        half_width = width / 2.0
        half_height = height / 2.0
        points = []
        for index in range(n_points):
            points.append(
                Point2D(
                    center.x + random.uniform(-half_width, half_width),
                    center.y + random.uniform(-half_height, half_height),
                    index,
                )
            )
        return points

    @staticmethod
    def on_rectangle(
        width: float, height: float, n_points: int = 100, center: Optional[Point2D] = None
    ) -> List[Point2D]:
        """Samples points uniformly from the boundary of a rectangle."""
        center = center or Point2D(0.0, 0.0)
        half_width = width / 2.0
        half_height = height / 2.0
        perimeter = 2 * (width + height)
        points = []
        for index in range(n_points):
            d = random.uniform(0, perimeter)
            if d < width:  # Bottom edge
                px, py = center.x - half_width + d, center.y - half_height
            elif d < width + height:  # Right edge
                px, py = center.x + half_width, center.y - half_height + (d - width)
            elif d < 2 * width + height:  # Top edge
                px, py = center.x + half_width - (d - width - height), center.y + half_height
            else:  # Left edge
                px, py = center.x - half_width, center.y + half_height - (d - 2 * width - height)
            points.append(Point2D(px, py, index))
        return points

    @staticmethod
    def in_triangle(a: Point2D, b: Point2D, c: Point2D, n_points: int = 100) -> List[Point2D]:
        """Samples points uniformly from the interior of a triangle."""
        from compgeom.polygon.polygon import generate_points_in_triangle

        return generate_points_in_triangle(a, b, c, n_points)

    @staticmethod
    def on_line_segment(p1: Point2D, p2: Point2D, n_points: int = 100) -> List[Point2D]:
        """Samples points uniformly from a line segment."""
        points = []
        dx, dy = p2.x - p1.x, p2.y - p1.y
        for index in range(n_points):
            t = random.random()
            points.append(Point2D(p1.x + t * dx, p1.y + t * dy, index))
        return points

    @staticmethod
    def in_cube(
        side_length: float, n_points: int = 100, center: Optional[Point3D] = None
    ) -> List[Point3D]:
        """Samples points uniformly from the interior of a cube."""
        center = center or Point3D(0.0, 0.0, 0.0)
        half_side = side_length / 2.0
        points = []
        for index in range(n_points):
            points.append(
                Point3D(
                    center.x + random.uniform(-half_side, half_side),
                    center.y + random.uniform(-half_side, half_side),
                    center.z + random.uniform(-half_side, half_side),
                    index,
                )
            )
        return points

    @staticmethod
    def on_sphere(center: Point3D, radius: float, n_points: int = 100) -> List[Point3D]:
        """Samples points uniformly from the surface of a sphere."""
        points = []
        for index in range(n_points):
            # Using Muller's method (standard normal distribution for uniform surface sampling)
            u = random.gauss(0, 1)
            v = random.gauss(0, 1)
            w = random.gauss(0, 1)
            norm = math.sqrt(u**2 + v**2 + w**2)
            if norm > 0:
                points.append(
                    Point3D(
                        center.x + radius * u / norm,
                        center.y + radius * v / norm,
                        center.z + radius * w / norm,
                        index,
                    )
                )
        return points


def generate_points_in_circle(center: Point2D, radius: float, n_points: int = 100) -> List[Point2D]:
    return PointSampler.in_circle(center, radius, n_points)


def generate_points_in_rectangle(
    width: float, height: float, n_points: int = 100, center: Optional[Point2D] = None
) -> List[Point2D]:
    return PointSampler.in_rectangle(width, height, n_points, center)


__all__ = [
    "PointSampler",
    "generate_points_in_circle",
    "generate_points_in_rectangle",
]
