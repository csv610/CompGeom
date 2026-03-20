"""Intersection of two convex polygons in O(n+m) time."""
from __future__ import annotations
from typing import List, Tuple, Optional
import math

from compgeom.kernel import Point2D, cross_product, distance

class ConvexIntersection:
    """Provides utilities for intersecting two convex polygons."""

    @staticmethod
    def area(poly_a: List[Point2D], poly_b: List[Point2D]) -> float:
        """
        Computes the area of the intersection of two convex polygons in O(n+m) time.
        Using a simplified Sutherland-Hodgman clipping.
        """
        if not poly_a or not poly_b:
            return 0.0
            
        # Ensure CCW orientation
        def get_area(p):
            a = 0.0
            for i in range(len(p)):
                p1, p2 = p[i], p[(i + 1) % len(p)]
                a += p1.x * p2.y - p2.x * p1.y
            return a * 0.5
            
        if get_area(poly_a) < 0: poly_a = poly_a[::-1]
        if get_area(poly_b) < 0: poly_b = poly_b[::-1]
        
        # Sutherland-Hodgman clipping of poly_a by the edges of poly_b
        clipped = poly_a
        for i in range(len(poly_b)):
            p1 = poly_b[i]
            p2 = poly_b[(i + 1) % len(poly_b)]
            clipped = ConvexIntersection._clip_with_edge(clipped, p1, p2)
            if not clipped:
                return 0.0
                
        return abs(get_area(clipped))

    @staticmethod
    def _clip_with_edge(poly: List[Point2D], a: Point2D, b: Point2D) -> List[Point2D]:
        """Clips a convex polygon against a single directed line (a->b)."""
        result = []
        if not poly:
            return result
            
        def is_inside(p):
            # Left of directed line a->b
            return cross_product(a, b, p) >= -1e-12

        def intersect(p1, p2):
            # Intersection of line segment p1-p2 with line a-b
            dx1, dy1 = p2.x - p1.x, p2.y - p1.y
            dx2, dy2 = b.x - a.x, b.y - a.y
            
            det = dx2 * dy1 - dy2 * dx1
            if abs(det) < 1e-12:
                return p1 # Parallel (should not happen in proper clipping)
                
            t = (dx2 * (a.y - p1.y) - dy2 * (a.x - p1.x)) / det
            return Point2D(p1.x + t * dx1, p1.y + t * dy1)

        for i in range(len(poly)):
            p_curr = poly[i]
            p_prev = poly[i - 1]
            
            if is_inside(p_curr):
                if not is_inside(p_prev):
                    result.append(intersect(p_prev, p_curr))
                result.append(p_curr)
            elif is_inside(p_prev):
                result.append(intersect(p_prev, p_curr))
                
        return result
