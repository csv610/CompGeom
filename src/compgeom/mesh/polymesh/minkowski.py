"""Minkowski Sum for 2D Polygons."""
import math
from typing import List

from ...kernel import Point2D

class MinkowskiSum:
    """Calculates the Minkowski sum of two convex polygons."""

    @staticmethod
    def _polar_angle(p1: Point2D, p2: Point2D) -> float:
        return math.atan2(p2.y - p1.y, p2.x - p1.x)

    @staticmethod
    def compute_convex(poly1: List[Point2D], poly2: List[Point2D]) -> List[Point2D]:
        """
        Computes the exact Minkowski sum of two convex polygons in O(N+M) time.
        Polygons must be ordered counter-clockwise.
        """
        if not poly1 or not poly2:
            return []

        # Find bottom-leftmost points
        def get_bottom_left(poly):
            min_idx = 0
            for i, p in enumerate(poly):
                if p.y < poly[min_idx].y or (p.y == poly[min_idx].y and p.x < poly[min_idx].x):
                    min_idx = i
            return min_idx

        i = get_bottom_left(poly1)
        j = get_bottom_left(poly2)

        n = len(poly1)
        m = len(poly2)

        # Ensure CCW orientation (simple check, assuming already convex)
        
        sum_poly = []
        
        # We need to process n + m vertices
        for _ in range(n + m):
            sum_poly.append(Point2D(poly1[i].x + poly2[j].x, poly1[i].y + poly2[j].y))
            
            p1_next = poly1[(i + 1) % n]
            p2_next = poly2[(j + 1) % m]
            
            # Edge vectors
            v1 = Point2D(p1_next.x - poly1[i].x, p1_next.y - poly1[i].y)
            v2 = Point2D(p2_next.x - poly2[j].x, p2_next.y - poly2[j].y)
            
            # Cross product to determine which edge is "further right"
            cross = v1.x * v2.y - v1.y * v2.x
            
            if cross > 1e-9:
                i = (i + 1) % n
            elif cross < -1e-9:
                j = (j + 1) % m
            else:
                # Parallel edges, advance both
                i = (i + 1) % n
                j = (j + 1) % m
                
        # Deduplicate
        unique_poly = []
        for p in sum_poly:
            if not unique_poly or (abs(p.x - unique_poly[-1].x) > 1e-9 or abs(p.y - unique_poly[-1].y) > 1e-9):
                unique_poly.append(p)
                
        if len(unique_poly) > 1 and abs(unique_poly[0].x - unique_poly[-1].x) < 1e-9 and abs(unique_poly[0].y - unique_poly[-1].y) < 1e-9:
            unique_poly.pop()
            
        return unique_poly
