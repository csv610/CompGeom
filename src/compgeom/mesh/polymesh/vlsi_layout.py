"""VLSI and Chip Design layout algorithms."""
from typing import List, Tuple

from ...kernel import Point2D

class VLSILayout:
    """Provides algorithms for Manhattan geometry and layout analysis."""

    @staticmethod
    def is_orthogonal(polygon: List[Point2D]) -> bool:
        """
        Checks if a polygon is rectilinear (Manhattan geometry).
        All edges must be strictly horizontal or vertical.
        """
        if len(polygon) < 4:
            return False
            
        n = len(polygon)
        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i+1)%n]
            
            dx = abs(p2.x - p1.x)
            dy = abs(p2.y - p1.y)
            
            if dx > 1e-9 and dy > 1e-9:
                return False # Diagonal edge found
                
        return True

    @staticmethod
    def manhattan_distance(p1: Point2D, p2: Point2D) -> float:
        """Calculates the L1 (Manhattan) distance between two points."""
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    @staticmethod
    def design_rule_check(poly1: List[Point2D], poly2: List[Point2D], min_clearance: float) -> bool:
        """
        Basic Design Rule Check (DRC).
        Returns False if the minimum distance between any vertex of poly1 and any vertex of poly2
        is less than the min_clearance using Manhattan distance.
        (Note: For a full DRC, edge-to-edge distance must also be checked).
        """
        for p1 in poly1:
            for p2 in poly2:
                if VLSILayout.manhattan_distance(p1, p2) < min_clearance:
                    return False
        return True
