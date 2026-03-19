"""Polygon vertex matching and reordering."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from compgeom.polygon.exceptions import PolygonError

if TYPE_CHECKING:
    from compgeom.polygon.polygon import Polygon

from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_similarity import get_polygon_signature


def reorder_to_match(
    poly1: Polygon, 
    poly2: Polygon, 
    allow_reflection: bool = True,
    auto_clean: bool = True
) -> list[Point2D]:
    """
    Reorders (cyclically shifts and potentially reverses) the vertices of poly2 
    to maximally match poly1 based on their geometric shape (similarity signature).
    """
    p1 = poly1
    p2 = poly2
    
    if auto_clean:
        p1 = p1.cleanup()
        p2 = p2.cleanup()
        
    if len(p1) != len(p2):
        raise PolygonError(
            f"Polygons must have the same number of vertices (after cleaning). "
            f"p1: {len(p1)}, p2: {len(p2)}"
        )
        
    n = len(p1)
    if n < 3:
        return list(poly2.vertices)
        
    sig1 = get_polygon_signature(p1)
    sig2 = get_polygon_signature(p2)
    
    if sig1 is None or sig2 is None:
        return list(poly2.vertices)
        
    def score_match(s1: list[tuple[float, float]], s2: list[tuple[float, float]]) -> float:
        error = 0.0
        for (side1, angle1), (side2, angle2) in zip(s1, s2):
            da = angle1 - angle2
            while da > math.pi: da -= 2 * math.pi
            while da < -math.pi: da += 2 * math.pi
            
            error += (side1 - side2)**2 + (da / (2 * math.pi))**2
        return error

    best_score = float('inf')
    best_shift = 0
    best_is_reflected = False

    for i in range(n):
        shifted_sig2 = sig2[i:] + sig2[:i]
        score = score_match(sig1, shifted_sig2)
        if score < best_score:
            best_score = score
            best_shift = i
            best_is_reflected = False
            
    if allow_reflection:
        rev_p2 = Polygon(list(reversed(p2.vertices)))
        sig2_rev = get_polygon_signature(rev_p2)
        
        if sig2_rev is not None:
            for i in range(n):
                shifted_sig2_rev = sig2_rev[i:] + sig2_rev[:i]
                score = score_match(sig1, shifted_sig2_rev)
                if score < best_score:
                    best_score = score
                    best_shift = i
                    best_is_reflected = True
                    
    source_vertices = list(p2.vertices)
    if best_is_reflected:
        source_vertices = list(reversed(source_vertices))
        
    reordered = source_vertices[best_shift:] + source_vertices[:best_shift]
    return reordered


__all__ = ["reorder_to_match"]
