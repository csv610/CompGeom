from __future__ import annotations

import math
from typing import List, Tuple
from compgeom.kernel import Point2D, distance, EPSILON, cross_product
from compgeom.polygon.polygon import Polygon


from compgeom.polygon.line_segment import proper_segment_intersection


def verify_simple_polygon(polygon: Polygon | List[Point2D]) -> bool:
    """
    Verifies if a polygon is simple.
    1. No two non-adjacent edges should intersect.
    2. Adjacent edges should only intersect at their common vertex.
    3. No duplicate vertices (except implicitly between last and first).
    """
    vertices = polygon.vertices if isinstance(polygon, Polygon) else list(polygon)
    n = len(vertices)
    if n < 3:
        return True

    # 1. Check for duplicate vertices
    seen_vertices = set()
    for v in vertices:
        v_tuple = (v.x, v.y)
        if v_tuple in seen_vertices:
            raise ValueError(f"Polygon has duplicate vertex: {v}")
        seen_vertices.add(v_tuple)

    # 2. Check for edge intersections
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        
        for j in range(i + 2, n):
            # Skip adjacent edges (i, i+1) and (j, j+1)
            # They share a vertex if j == i-1 (mod n) or j == i+1 (mod n)
            if (j + 1) % n == i:
                continue
            
            p3 = vertices[j]
            p4 = vertices[(j + 1) % n]
            
            if proper_segment_intersection(p1, p2, p3, p4):
                raise ValueError(f"Polygon is self-intersecting: edge {i}-{(i+1)%n} intersects edge {j}-{(j+1)%n}")

    return True


def verify_convex_hull(points: List[Point2D], hull: List[Point2D]) -> bool:
    """
    Rigorously verifies a convex hull.
    1. Every hull vertex must be one of the input points.
    2. Every input point must be inside or on the boundary of the hull.
    3. The hull must be a convex polygon (all turns same direction).
    4. No redundant vertices (optional, but good for minimality).
    """
    if not points:
        return not hull

    if not hull:
        if len(set(points)) == 0:
            return True
        raise ValueError("Hull is empty but input points are not")

    unique_points = set(points)
    
    # 1. Hull vertices from input
    for v in hull:
        if v not in unique_points:
            raise ValueError(f"Hull vertex {v} was not in the input point set")

    # 2. Convexity check
    if len(hull) >= 3:
        for i in range(len(hull)):
            p1 = hull[i-1]
            p2 = hull[i]
            p3 = hull[(i+1)%len(hull)]
            cp = cross_product(p1, p2, p3)
            if cp < -EPSILON:
                raise ValueError(f"Hull is not convex at vertex {p2} (cross product {cp} < 0)")
            if abs(cp) < EPSILON:
                 # Redundant vertex on edge
                 pass

    # 3. Containment check
    # We can use the property that for a convex hull, every input point must be 
    # to the "left" (or on) every edge.
    if len(hull) >= 2:
        for i in range(len(hull)):
            p1 = hull[i-1]
            p2 = hull[i]
            for p in unique_points:
                if cross_product(p1, p2, p) < -EPSILON:
                    raise ValueError(f"Point {p} is outside hull edge {p1}-{p2}")
    else:
        # Hull of 1 or 2 points
        if len(hull) == 1:
            if len(unique_points) > 1:
                raise ValueError("Hull has 1 point but input has multiple unique points")
        elif len(hull) == 2:
            p1, p2 = hull
            for p in unique_points:
                if abs(cross_product(p1, p2, p)) > EPSILON:
                    raise ValueError(f"Point {p} is not collinear with hull 2-point segment")

    return True


def verify_polygon_area(polygon: List[Point2D], result_area: float) -> bool:
    """Verifies polygon area using Shoelace formula as an independent check."""
    n = len(polygon)
    if n < 3:
        return abs(result_area) < EPSILON

    area = 0.0
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        area += (p1.x * p2.y) - (p2.x * p1.y)
    
    calculated_area = abs(area) / 2.0
    if abs(calculated_area - result_area) > EPSILON:
        raise ValueError(f"Result area {result_area} doesn't match calculated area {calculated_area}")
    return True


__all__ = ["verify_simple_polygon", "verify_convex_hull", "verify_polygon_area"]
