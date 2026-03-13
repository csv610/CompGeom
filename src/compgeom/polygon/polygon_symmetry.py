"""Tools for orienting polygons for symmetry."""

from __future__ import annotations

import math
from typing import Sequence

from ..kernel import Point2D
from .polygon import Polygon
from .polygon_utils import rotate_polygon


def get_moments(vertices: Sequence[Point2D]) -> tuple[float, float, float, float]:
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
    Aligns the principal axis of inertia with the y-axis.
    """
    vertices = polygon.as_list()
    if len(vertices) < 3:
        return polygon

    # 1. Get properties and translate to centroid
    props = polygon.properties()
    area = props.area
    centroid = props.centroid
    
    translated_vertices = [
        Point2D(p.x - centroid.x, p.y - centroid.y) for p in vertices
    ]
    
    # 2. Calculate moments of inertia about the centroid
    # Re-calculate to be sure we are at centroid
    _, ix, iy, ixy = get_moments(translated_vertices)
    
    # 3. Find principal axis angle
    # tan(2*theta) = 2*Ixy / (Iy - Ix)
    denom = iy - ix
    if abs(denom) < 1e-12:
        if abs(ixy) < 1e-12:
            theta = 0.0
        else:
            theta = math.pi / 4.0
    else:
        theta = 0.5 * math.atan2(2 * ixy, denom)
    
    # We want to align a principal axis with the Y-axis.
    # The current principal axis is at angle theta.
    # To bring it to Y-axis (pi/2), we need to rotate by (pi/2 - theta).
    
    # Candidate 1: Aligns principal axis with X
    pts1 = rotate_polygon(translated_vertices, -theta, Point2D(0, 0))
    
    # Candidate 2: Aligns principal axis with Y
    pts2 = rotate_polygon(pts1, math.pi / 2, Point2D(0, 0))

    def calculate_asymmetry_y(pts: list[Point2D]) -> float:
        # Sum of x-coordinates should be 0 for a symmetric-ish shape
        # but also we want the "spread" to be balanced.
        # A better measure: sum of distances of reflected points to the original points
        # For simplicity, let's just check the sum of cubes of x-coordinates.
        # For a symmetric shape, sum x^3 = 0.
        return abs(sum(p.x**3 for p in pts))

    if calculate_asymmetry_y(pts1) < calculate_asymmetry_y(pts2):
        final_vertices = pts1
    else:
        final_vertices = pts2

    return Polygon(final_vertices)
