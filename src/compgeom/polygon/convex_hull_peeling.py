"""Convex Hull Peeling (Onion Peeling) algorithm."""

from __future__ import annotations

from typing import List
from compgeom.kernel import Point2D
from compgeom.polygon.convex_hull import ConvexHull

def convex_hull_peeling(points: List[Point2D], algorithm: str = "scipy") -> List[List[Point2D]]:
    """
    Computes the convex hull peeling (onion peeling) of a set of 2D points.
    Repeatedly finds the convex hull, removes its vertices, and continues until no points remain.

    Args:
        points: A list of Point2D objects.
        algorithm: The algorithm to use for convex hull generation.

    Returns:
        A list of hulls, where each hull is a list of Point2D objects representing a layer.
    """
    remaining_points = list(set(points))
    layers = []

    while remaining_points:
        if len(remaining_points) <= 2:
            layers.append(remaining_points)
            break
            
        # Generate the current hull
        hull = ConvexHull.generate(remaining_points, algorithm=algorithm)
        layers.append(hull)
        
        # Remove hull points from the set of remaining points
        hull_set = set(hull)
        remaining_points = [p for p in remaining_points if p not in hull_set]
        
    return layers

__all__ = ["convex_hull_peeling"]
