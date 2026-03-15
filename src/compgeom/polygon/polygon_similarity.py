"""Polygon similarity check helper."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from .polygon import Polygon

from ..kernel import distance
from .tolerance import is_zero, EPSILON


def get_polygon_signature(polygon: Polygon) -> list[tuple[float, float]] | None:
    """
    Computes a similarity signature for a polygon.
    The signature consists of a sequence of (normalized side length, turning angle) for each vertex.
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

        side_lengths.append(distance(p_curr, p_next))

        ux, uy = p_curr.x - p_prev.x, p_curr.y - p_prev.y
        vx, vy = p_next.x - p_curr.x, p_next.y - p_curr.y

        cross = ux * vy - uy * vx
        dot = ux * vx + uy * vy
        
        if is_zero(ux, 1e-12) and is_zero(uy, 1e-12):
             angles.append(0.0)
        elif is_zero(vx, 1e-12) and is_zero(vy, 1e-12):
             angles.append(0.0)
        else:
             angles.append(math.atan2(cross, dot))

    perimeter = sum(side_lengths)
    if is_zero(perimeter, 1e-12):
        return None

    normalized_sides = [s / perimeter for s in side_lengths]
    return list(zip(normalized_sides, angles))


def polygons_are_similar(
    poly1: Polygon, poly2: Polygon, tolerance: float = EPSILON, auto_clean: bool = True
) -> bool:
    """
    Checks if two polygons are similar.
    Similarity is invariant under translation, rotation, scaling, and reflection.
    """
    from .polygon import Polygon

    if auto_clean:
        poly1 = poly1.cleanup()
        poly2 = poly2.cleanup()

    if len(poly1) != len(poly2):
        return False

    sig1 = get_polygon_signature(poly1)
    sig2 = get_polygon_signature(poly2)

    if sig1 is None or sig2 is None:
        return sig1 == sig2

    n = len(sig1)

    def compare(s1: list[tuple[float, float]], s2: list[tuple[float, float]]) -> bool:
        for (side1, angle1), (side2, angle2) in zip(s1, s2):
            if abs(side1 - side2) > tolerance or abs(angle1 - angle2) > tolerance:
                return False
        return True

    for i in range(n):
        shifted_sig2 = sig2[i:] + sig2[:i]
        if compare(sig1, shifted_sig2):
            return True

    rev_poly2 = Polygon(list(reversed(poly2.vertices)))
    sig2_rev = get_polygon_signature(rev_poly2)
    
    if sig2_rev is not None:
        for i in range(n):
            shifted_sig2_rev = sig2_rev[i:] + sig2_rev[:i]
            if compare(sig1, shifted_sig2_rev):
                return True

    return False


__all__ = ["get_polygon_signature", "polygons_are_similar"]
