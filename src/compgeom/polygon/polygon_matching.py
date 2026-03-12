"""Polygon vertex matching and reordering."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from .polygon import Polygon

from ..kernel import Point
from .polygon_utils import cleanup_polygon
from .polygon_similarity import get_similarity_signature


def reorder_to_match(
    poly1: Polygon, 
    poly2: Polygon, 
    allow_reflection: bool = True,
    auto_clean: bool = True
) -> list[Point]:
    """
    Reorders (cyclically shifts and potentially reverses) the vertices of poly2 
    to maximally match poly1 based on their geometric shape (similarity signature).
    
    Args:
        poly1: The reference polygon.
        poly2: The polygon whose vertices should be reordered.
        allow_reflection: If True, considers reversed vertex orders if they match better.
        auto_clean: If True, cleans both polygons (removes redundant points) 
                    before matching.
                    
    Returns:
        A list of vertices for poly2 in the optimal order.
    """
    # Importing Polygon here to avoid circular dependency
    from .polygon import Polygon
    
    p1 = poly1
    p2 = poly2
    
    if auto_clean:
        p1 = Polygon(cleanup_polygon(list(p1.vertices)))
        p2 = Polygon(cleanup_polygon(list(p2.vertices)))
        
    if len(p1) != len(p2):
        raise ValueError(
            f"Polygons must have the same number of vertices (after cleaning). "
            f"p1: {len(p1)}, p2: {len(p2)}"
        )
        
    n = len(p1)
    if n < 3:
        return list(poly2.vertices)
        
    sig1 = get_similarity_signature(p1)
    sig2 = get_similarity_signature(p2)
    
    if sig1 is None or sig2 is None:
        return list(poly2.vertices)
        
    def score_match(s1: list[tuple[float, float]], s2: list[tuple[float, float]]) -> float:
        # Lower score is better (Mean Squared Error)
        error = 0.0
        for (side1, angle1), (side2, angle2) in zip(s1, s2):
            # Normalize angle difference to [-pi, pi]
            da = angle1 - angle2
            while da > math.pi: da -= 2 * math.pi
            while da < -math.pi: da += 2 * math.pi
            
            error += (side1 - side2)**2 + (da / (2 * math.pi))**2
        return error

    best_score = float('inf')
    best_shift = 0
    best_is_reflected = False

    # Signature-based matching is invariant to translation, rotation, scale.
    # We find the shift i such that p2_reordered[j] corresponds to p1[j]
    
    # Check all cyclic shifts of p2's signature
    for i in range(n):
        # Mapping: p1[j] corresponds to p2[(j+i)%n]
        shifted_sig2 = sig2[i:] + sig2[:i]
        score = score_match(sig1, shifted_sig2)
        if score < best_score:
            best_score = score
            best_shift = i
            best_is_reflected = False
            
    # Check reflection
    if allow_reflection:
        rev_v2 = list(reversed(p2.vertices))
        rev_p2 = Polygon(rev_v2)
        sig2_rev = get_similarity_signature(rev_p2)
        
        if sig2_rev is not None:
            for i in range(n):
                shifted_sig2_rev = sig2_rev[i:] + sig2_rev[:i]
                score = score_match(sig1, shifted_sig2_rev)
                if score < best_score:
                    best_score = score
                    best_shift = i
                    best_is_reflected = True
                    
    # Construct the reordered vertex list
    source_vertices = list(p2.vertices)
    if best_is_reflected:
        source_vertices = list(reversed(source_vertices))
        
    # Apply the best cyclic shift
    # If best_shift = k, then p1[0] matched sig2[k]
    # sig2[k] is the signature at vertex k.
    reordered = source_vertices[best_shift:] + source_vertices[:best_shift]
    return reordered
