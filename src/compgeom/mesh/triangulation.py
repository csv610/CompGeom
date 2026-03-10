"""Triangulation, Delaunay, and Voronoi algorithms."""

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
    build_topology,
    constrained_delaunay_triangulation,
    delaunay_flip,
    get_nondelaunay_triangles,
    is_delaunay,
    triangulate,
    triangulate_divide_and_conquer,
)


def get_voronoi_cells(points: list[Point], boundary_polygon: list[Point]):
    cells = []
    for point in points:
        cell = list(boundary_polygon)
        for other in points:
            if point == other:
                continue
            midpoint = Point((point.x + other.x) / 2, (point.y + other.y) / 2)
            direction = sub(other, point)
            bisector_end = Point(midpoint.x - direction.y, midpoint.y + direction.x)
            if cross_product(midpoint, bisector_end, point) < 0:
                cell = clip_polygon(cell, bisector_end, midpoint)
            else:
                cell = clip_polygon(cell, midpoint, bisector_end)
        cells.append((point, cell))
    return cells


def get_square_boundary(size=100, center=(50, 50)):
    cx, cy = center
    half_size = size / 2
    return [
        Point(cx - half_size, cy - half_size),
        Point(cx + half_size, cy - half_size),
        Point(cx + half_size, cy + half_size),
        Point(cx - half_size, cy + half_size),
    ]


def get_circle_boundary(radius=50, center=(50, 50), n_segments=64):
    cx, cy = center
    return [
        Point(cx + radius * math.cos(2 * math.pi * index / n_segments), cy + radius * math.sin(2 * math.pi * index / n_segments))
        for index in range(n_segments)
    ]


__all__ = [
    "DTriangle",
    "DelaunayMesher",
    "DynamicDelaunay",
    "MeshTriangle",
    "Triangle",
    "constrained_delaunay_triangulation",
    "build_topology",
    "delaunay_flip",
    "get_circle_boundary",
    "get_nondelaunay_triangles",
    "get_square_boundary",
    "get_voronoi_cells",
    "is_delaunay",
    "triangulate",
    "triangulate_divide_and_conquer",
]
