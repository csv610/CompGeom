"""Polygon similarity check helper."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .polygon import Polygon

from ..kernel import distance
from .polygon_utils import cleanup_polygon


def get_similarity_signature(polygon: Polygon) -> list[tuple[float, float]] | None:
    """
    Computes a similarity signature for a polygon.
    The signature consists of a sequence of (normalized side length, turning angle) for each vertex.
    
    Args:
        polygon: The polygon to signature.
        
    Returns:
        A list of (side_length_ratio, turning_angle) tuples, or None if the polygon is degenerate.
    """
    vertices = polygon.vertices
    n = len(vertices)
    if n < 3:
        return None

    side_lengths = []
    angles = []

    for i in range(n):
        p_prev = vertices[i - 1]
        p_curr = vertices[i]
        p_next = vertices[(i + 1) % n]

        # Side length from p_curr to p_next
        side_lengths.append(distance(p_curr, p_next))

        # Turning angle at p_curr
        # Vector u from p_prev to p_curr
        ux, uy = p_curr.x - p_prev.x, p_curr.y - p_prev.y
        # Vector v from p_curr to p_next
        vx, vy = p_next.x - p_curr.x, p_next.y - p_curr.y

        # angle = atan2(cross, dot)
        cross = ux * vy - uy * vx
        dot = ux * vx + uy * vy
        
        # Handle zero length vectors to avoid atan2(0,0) issues if possible, 
        # though degenerate cases are mostly handled by perimeter check.
        if abs(ux) < 1e-12 and abs(uy) < 1e-12:
             angles.append(0.0)
        elif abs(vx) < 1e-12 and abs(vy) < 1e-12:
             angles.append(0.0)
        else:
             angles.append(math.atan2(cross, dot))

    perimeter = sum(side_lengths)
    if perimeter < 1e-12:
        return None

    normalized_sides = [s / perimeter for s in side_lengths]
    return list(zip(normalized_sides, angles))


def are_similar(
    poly1: Polygon, poly2: Polygon, tolerance: float = 1e-7, auto_clean: bool = True
) -> bool:
    """
    Checks if two polygons are similar.
    Similarity is invariant under translation, rotation, scaling, and reflection.

    Args:
        poly1: First polygon.
        poly2: Second polygon.
        tolerance: Float tolerance for comparisons.
        auto_clean: If True, simplifies polygons by removing redundant collinear points
                    before comparison.

    Returns:
        True if the polygons are similar, False otherwise.
    """
    # Importing Polygon here to avoid circular dependency
    from .polygon import Polygon

    if auto_clean:
        poly1 = Polygon(cleanup_polygon(list(poly1.vertices)))
        poly2 = Polygon(cleanup_polygon(list(poly2.vertices)))

    if len(poly1) != len(poly2):
        return False

    sig1 = get_similarity_signature(poly1)
    sig2 = get_similarity_signature(poly2)

    if sig1 is None or sig2 is None:
        return sig1 == sig2

    n = len(sig1)

    def compare(s1: list[tuple[float, float]], s2: list[tuple[float, float]]) -> bool:
        for (side1, angle1), (side2, angle2) in zip(s1, s2):
            if abs(side1 - side2) > tolerance or abs(angle1 - angle2) > tolerance:
                return False
        return True

    # Check all cyclic shifts for the original orientation
    for i in range(n):
        shifted_sig2 = sig2[i:] + sig2[:i]
        if compare(sig1, shifted_sig2):
            return True

    # Check all cyclic shifts for the reflected orientation
    rev_poly2 = Polygon(list(reversed(poly2.vertices)))
    sig2_rev = get_similarity_signature(rev_poly2)
    
    if sig2_rev is not None:
        for i in range(n):
            shifted_sig2_rev = sig2_rev[i:] + sig2_rev[:i]
            if compare(sig1, shifted_sig2_rev):
                return True

    return False
