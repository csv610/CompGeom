"""2D Polygon Boolean operations (Clipping)."""
from typing import List, Tuple
import math

from ...kernel import Point

class PolygonBooleans:
    """Provides Union, Intersection, and Difference for 2D polygons."""

    @staticmethod
    def boolean_operation(poly_a: List[Point], poly_b: List[Point], operation: str = 'union') -> List[List[Point]]:
        """
        Performs a 2D boolean operation using a simplified clipping approach.
        In a full industrial version, the Sutherland-Hodgman or Weiler-Atherton algorithm
        would be implemented with robust intersection handling.
        """
        try:
            import numpy as np
            from shapely.geometry import Polygon
        except ImportError:
            # Fallback or error
            raise ImportError("Polygon Booleans require 'shapely'.")

        p_a = Polygon([(p.x, p.y) for p in poly_a])
        p_b = Polygon([(p.x, p.y) for p in poly_b])
        
        res = None
        if operation == 'union':
            res = p_a.union(p_b)
        elif operation == 'intersection':
            res = p_a.intersection(p_b)
        elif operation == 'difference':
            res = p_a.difference(p_b)
            
        if res.is_empty:
            return []
            
        # Handle MultiPolygon results
        from shapely.geometry import MultiPolygon
        polys = [res] if not isinstance(res, MultiPolygon) else list(res.geoms)
        
        output = []
        for p in polys:
            coords = list(p.exterior.coords)
            if coords[0] == coords[-1]: coords.pop()
            output.append([Point(c[0], c[1]) for c in coords])
            
        return output

    @staticmethod
    def union(poly_a: List[Point], poly_b: List[Point]) -> List[List[Point]]:
        return PolygonBooleans.boolean_operation(poly_a, poly_b, 'union')

    @staticmethod
    def intersection(poly_a: List[Point], poly_b: List[Point]) -> List[List[Point]]:
        return PolygonBooleans.boolean_operation(poly_a, poly_b, 'intersection')

    @staticmethod
    def difference(poly_a: List[Point], poly_b: List[Point]) -> List[List[Point]]:
        return PolygonBooleans.boolean_operation(poly_a, poly_b, 'difference')
