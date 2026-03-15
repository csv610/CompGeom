"""Tools for orienting polygons for symmetry."""

from __future__ import annotations

import math
from typing import Sequence

from ..kernel import Point2D
from .polygon import Polygon


def get_polygon_moments(vertices: Sequence[Point2D]) -> tuple[float, float, float, float]:
    """Calculate area and moments of inertia (Ix, Iy, Ixy) about the origin."""
    n = len(vertices)
    area = 0.0
    ix = 0.0
    iy = 0.0
    ixy = 0.0

    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        
        common = p1.x * p2.y - p2.x * p1.y
        area += common
        ix += (p1.y**2 + p1.y * p2.y + p2.y**2) * common
        iy += (p1.x**2 + p1.x * p2.x + p2.x**2) * common
        ixy += (p1.x * p2.y + 2 * p1.x * p1.y + 2 * p2.x * p2.y + p2.x * p1.y) * common

    area /= 2.0
    ix /= 12.0
    iy /= 12.0
    ixy /= 24.0
    
    return area, ix, iy, ixy


def orient_polygon_for_symmetry(polygon: Polygon) -> Polygon:
    """
    Orients the polygon about its centroid to provide maximum symmetry about the y-axis.
    """
    vertices = polygon.vertices
    if len(vertices) < 3:
        return polygon

    props = polygon.properties()
    centroid = props.centroid
    
    translated_vertices = [
        Point2D(p.x - centroid.x, p.y - centroid.y) for p in vertices
    ]
    
    _, ix, iy, ixy = get_polygon_moments(translated_vertices)
    
    denom = iy - ix
    if abs(denom) < 1e-12:
        theta = 0.0 if abs(ixy) < 1e-12 else math.pi / 4.0
    else:
        theta = 0.5 * math.atan2(2 * ixy, denom)
    
    # Candidate 1: Aligns principal axis with X
    poly_translated = Polygon(translated_vertices)
    pts1 = poly_translated.rotate(-theta, Point2D(0, 0)).as_list()
    
    # Candidate 2: Aligns principal axis with Y
    pts2 = Polygon(pts1).rotate(math.pi / 2, Point2D(0, 0)).as_list()

    def calculate_asymmetry_y(pts: list[Point2D]) -> float:
        return abs(sum(p.x**3 for p in pts))

    if calculate_asymmetry_y(pts1) < calculate_asymmetry_y(pts2):
        final_vertices = pts1
    else:
        final_vertices = pts2

    return Polygon(final_vertices)


__all__ = ["get_polygon_moments", "orient_polygon_for_symmetry"]
