from __future__ import annotations

import math
from typing import List, Tuple
from compgeom.kernel import Point2D, Transformation, EPSILON
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_similarity import polygons_are_similar, get_polygon_signature


def verify_polygon_similarity(poly1: Polygon, poly2: Polygon, result: bool) -> bool:
    """
    Rigorously verifies the polygon similarity result.
    1. Consistency: Result must match polygons_are_similar(poly1, poly2).
    2. Identity (Paranoid): A polygon must be similar to itself.
    3. Transformation Invariance (Paranoid): Similar polygons must remain similar 
       under translation, rotation, scaling, and reflection.
    4. Symmetry (Paranoid): sim(A, B) == sim(B, A).
    """
    # 1. Basic consistency
    actual = polygons_are_similar(poly1, poly2)
    if actual != result:
        raise ValueError(f"Similarity result {result} does not match expected {actual}")

    # 2. Symmetry check
    if polygons_are_similar(poly2, poly1) != result:
        raise ValueError("Similarity is not symmetric")

    # 3. Identity and Transformation Invariance (only if result is True)
    if result:
        # Self-similarity
        if not polygons_are_similar(poly1, poly1):
            raise ValueError("Polygon is not similar to itself")

        # Translation
        t = Transformation.translation(100.0, -50.0)
        poly1_t = Polygon([t.apply_to_point2d(p) for p in poly1.vertices])
        if not polygons_are_similar(poly1, poly1_t):
            raise ValueError("Similarity is not invariant under translation")

        # Rotation
        r = Transformation.rotation_z(math.pi / 4.0)
        poly1_r = Polygon([r.apply_to_point2d(p) for p in poly1.vertices])
        if not polygons_are_similar(poly1, poly1_r):
            raise ValueError("Similarity is not invariant under rotation")

        # Scaling
        s = Transformation.scale(2.5, 2.5)
        poly1_s = Polygon([s.apply_to_point2d(p) for p in poly1.vertices])
        if not polygons_are_similar(poly1, poly1_s):
            raise ValueError("Similarity is not invariant under scaling")

        # Reflection (Scaling with -1)
        ref = Transformation.scale(-1.0, 1.0)
        poly1_ref = Polygon([ref.apply_to_point2d(p) for p in poly1.vertices])
        if not polygons_are_similar(poly1, poly1_ref):
            raise ValueError("Similarity is not invariant under reflection")

    return True
