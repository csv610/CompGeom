"""Triangulation and Voronoi algorithms."""

from __future__ import annotations

import math

from ..geo_math.geometry import (
    Point,
    clip_polygon,
    cross_product,
    sub,
)
from .delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    Triangle,
)


class VoronoiDiagram:
    """
    Computes and stores a Voronoi Diagram for a set of points within a boundary.
    """

    def __init__(self, points: list[Point], boundary: list[Point]):
        self.points = points
        self.boundary = boundary
        self.cells: list[tuple[Point, list[Point]]] = []

    def compute(self) -> list[tuple[Point, list[Point]]]:
        """
        Computes the Voronoi cells using a clipping algorithm.
        Returns a list of tuples (site_point, cell_polygon).
        """
        self.cells = []
        for point in self.points:
            cell = list(self.boundary)
            for other in self.points:
                if point == other:
                    continue
                midpoint = Point((point.x + other.x) / 2, (point.y + other.y) / 2)
                direction = sub(other, point)
                bisector_end = Point(midpoint.x - direction.y, midpoint.y + direction.x)
                if cross_product(midpoint, bisector_end, point) < 0:
                    cell = clip_polygon(cell, bisector_end, midpoint)
                else:
                    cell = clip_polygon(cell, midpoint, bisector_end)
            self.cells.append((point, cell))
        return self.cells

    @staticmethod
    def get_square_boundary(size: float = 100, center: tuple[float, float] = (50, 50)) -> list[Point]:
        """Generates a square boundary polygon."""
        cx, cy = center
        half_size = size / 2
        return [
            Point(cx - half_size, cy - half_size),
            Point(cx + half_size, cy - half_size),
            Point(cx + half_size, cy + half_size),
            Point(cx - half_size, cy + half_size),
        ]

    @staticmethod
    def get_circle_boundary(radius: float = 50, center: tuple[float, float] = (50, 50), n_segments: int = 64) -> list[Point]:
        """Generates a circular boundary polygon."""
        cx, cy = center
        return [
            Point(cx + radius * math.cos(2 * math.pi * index / n_segments), 
                  cy + radius * math.sin(2 * math.pi * index / n_segments))
            for index in range(n_segments)
        ]


__all__ = [
    "DTriangle",
    "DelaunayMesher",
    "DynamicDelaunay",
    "MeshTriangle",
    "Triangle",
    "VoronoiDiagram",
]
