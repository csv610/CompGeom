"""Polygon Boolean operations (inspired by Boost.Polygon)."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import List, Optional, Tuple

from ..kernel import Point2D, is_on_segment, cross_product
from .polygon import Polygon
from .tolerance import are_close, is_zero, EPSILON


def verify_boolean_op(poly_a: Polygon, poly_b: Polygon, results: List[Polygon], op: str) -> bool:
    """Verify the results of boolean operations using area properties."""
    area_a = poly_a.area
    area_b = poly_b.area
    area_res = sum(p.area for p in results)

    # Basic area checks for sanity
    if op == "union":
        return area_res <= area_a + area_b + EPSILON
    elif op == "intersection":
        return area_res <= min(area_a, area_b) + EPSILON
    elif op == "difference":
        return area_res <= area_a + EPSILON
    elif op == "xor":
        return area_res <= area_a + area_b + EPSILON
    return True


def polygon_union(poly_a: Polygon, poly_b: Polygon) -> List[Polygon]:
    """Return the union of two polygons (A ∪ B)."""
    return _apply_boolean_op(poly_a, poly_b, "union")


def polygon_intersection(poly_a: Polygon, poly_b: Polygon) -> List[Polygon]:
    """Return the intersection of two polygons (A ∩ B)."""
    return _apply_boolean_op(poly_a, poly_b, "intersection")


def polygon_difference(poly_a: Polygon, poly_b: Polygon) -> List[Polygon]:
    """Return the difference of two polygons (A - B)."""
    return _apply_boolean_op(poly_a, poly_b, "difference")


def polygon_xor(poly_a: Polygon, poly_b: Polygon) -> List[Polygon]:
    """Return the symmetric difference of two polygons (A ⊕ B)."""
    return _apply_boolean_op(poly_a, poly_b, "xor")


def _apply_boolean_op(poly_a: Polygon, poly_b: Polygon, op: str) -> List[Polygon]:
    """Generic implementation of polygon boolean operations using segment clipping."""
    if not poly_a:
        results = [poly_b] if op in ("union", "xor") and poly_b else []
        return results
    if not poly_b:
        results = [poly_a] if op in ("union", "difference", "xor") and poly_a else []
        return results

    # Ensure consistent orientation (CCW)
    poly_a_ccw = poly_a.ensure_ccw()
    poly_b_ccw = poly_b.ensure_ccw()

    # 1. Subdivide edges of both polygons at all intersection points
    # This is done in a single pass to avoid duplicated work.
    edges_a, edges_b = _subdivide_all_edges(poly_a_ccw.vertices, poly_b_ccw.vertices)

    # 2. Filter edges based on the operation
    kept_edges = []

    # Convert edges_b to a set of keys for O(1) matching
    def to_key(p): return (round(p.x, 10), round(p.y, 10))
    edges_b_set = set((to_key(e1), to_key(e2)) for e1, e2 in edges_b)
    edges_b_rev_set = set((to_key(e2), to_key(e1)) for e1, e2 in edges_b)

    # We can optimize by pre-calculating segment status
    for p1, p2 in edges_a:
        status = _classify_segment(p1, p2, poly_b_ccw)
        edge_key = (to_key(p1), to_key(p2))
        
        if op == "union":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # For union, keep only one if they have same direction. 
                # If they have opposite direction, both are internal, so drop.
                if edge_key in edges_b_set:
                    kept_edges.append((p1, p2))
        elif op == "intersection":
            if status == "inside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # For intersection, keep if they have same direction.
                if edge_key in edges_b_set:
                    kept_edges.append((p1, p2))
        elif op == "difference":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # If opposite direction, it stays on boundary. If same direction, it's internal.
                if edge_key in edges_b_rev_set:
                     kept_edges.append((p1, p2))
        elif op == "xor":
            if status == "outside":
                kept_edges.append((p1, p2))

    # Re-check against edges_a for edges_b
    edges_a_set = set((to_key(e1), to_key(e2)) for e1, e2 in edges_a)
    edges_a_rev_set = set((to_key(e2), to_key(e1)) for e1, e2 in edges_a)

    for p1, p2 in edges_b:
        status = _classify_segment(p1, p2, poly_a_ccw)
        edge_key = (to_key(p1), to_key(p2))
        
        if op == "union":
            if status == "outside":
                kept_edges.append((p1, p2))
        elif op == "intersection":
            if status == "inside":
                kept_edges.append((p1, p2))
        elif op == "difference":
            if status == "inside":
                # For A-B, segments of B inside A are reversed
                kept_edges.append((p2, p1))
        elif op == "xor":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "inside":
                kept_edges.append((p2, p1))
            elif status == "on_boundary":
                # If same direction or opposite direction on boundary, XOR usually drops them
                # because they are in both or touch.
                pass

    # 3. Reconstruct polygons from kept edges
    results = _reconstruct_polygons(kept_edges)

    # 4. Verification
    verify_boolean_op(poly_a, poly_b, results, op)

    return results


def _subdivide_all_edges(poly_a: Tuple[Point2D, ...], poly_b: Tuple[Point2D, ...]) -> Tuple[List[Tuple[Point2D, Point2D]], List[Tuple[Point2D, Point2D]]]:
    """Split edges of both polygons at all points where they intersect."""
    n, m = len(poly_a), len(poly_b)
    
    # Track points to be added to each edge
    points_on_a = [set([poly_a[i], poly_a[(i + 1) % n]]) for i in range(n)]
    points_on_b = [set([poly_b[j], poly_b[(j + 1) % m]]) for j in range(m)]

    for i in range(n):
        p1, p2 = poly_a[i], poly_a[(i + 1) % n]
        for j in range(m):
            q1, q2 = poly_b[j], poly_b[(j + 1) % m]
            
            # Check for intersection
            intersect = _intersect_segments(p1, p2, q1, q2)
            if intersect:
                points_on_a[i].add(intersect)
                points_on_b[j].add(intersect)
            
            # Check for endpoints of B on A
            if is_on_segment(q1, p1, p2): points_on_a[i].add(q1)
            if is_on_segment(q2, p1, p2): points_on_a[i].add(q2)
            
            # Check for endpoints of A on B
            if is_on_segment(p1, q1, q2): points_on_b[j].add(p1)
            if is_on_segment(p2, q1, q2): points_on_b[j].add(p2)

    def build_edges(poly, points_on_edges):
        subdivided = []
        for i in range(len(poly)):
            start_pt = poly[i]
            # Sort points by distance from start_pt
            pts = sorted(list(points_on_edges[i]), key=lambda p: (p.x - start_pt.x)**2 + (p.y - start_pt.y)**2)
            for k in range(len(pts) - 1):
                # Manual comparison since we want to avoid same_point import if possible, 
                # but it's needed for robustness.
                if not are_close(pts[k], pts[k+1], EPSILON):
                    subdivided.append((pts[k], pts[k+1]))
        return subdivided

    return build_edges(poly_a, points_on_a), build_edges(poly_b, points_on_b)


def _intersect_segments(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Optional[Point2D]:
    """Find the intersection point of two line segments using a robust formula."""
    # Using a slightly larger epsilon for denominator to handle near-parallel lines
    denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if is_zero(denom, 1e-12):
        return None

    # Intersection point using Cramer's rule
    px = ((p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)) / denom
    py = ((p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)) / denom

    intersect = Point2D(px, py)

    # Ensure the intersection point is actually on both segments
    if is_on_segment(intersect, p1, p2) and is_on_segment(intersect, p3, p4):
        return intersect
    return None


def _classify_segment(p1: Point2D, p2: Point2D, poly: Polygon) -> str:
    """Classify a segment as 'inside', 'outside', or 'on_boundary' of a polygon."""
    mid = Point2D((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
    
    # Check boundary first as it's more specific
    if poly.point_on_boundary(mid):
        return "on_boundary"
    
    # contains_point handles the 'inside' case
    if poly.contains_point(mid):
        return "inside"
    
    return "outside"


def _reconstruct_polygons(edges: List[Tuple[Point2D, Point2D]]) -> List[Polygon]:
    """Assemble a list of segments into closed polygons."""
    if not edges:
        return []

    # Map each start point to its possible end points
    # Using a small rounding to handle floating point jitter in dictionary keys
    def to_key(p): return (round(p.x, 10), round(p.y, 10))
    
    graph = defaultdict(list)
    for p1, p2 in edges:
        graph[to_key(p1)].append(p2)

    polygons = []
    used_edges = set()

    for start_edge_p1, start_edge_p2 in edges:
        edge_id = (to_key(start_edge_p1), to_key(start_edge_p2))
        if edge_id in used_edges:
            continue

        current_poly = [start_edge_p1]
        curr = start_edge_p2
        used_edges.add(edge_id)
        
        # Safety limit to prevent infinite loops
        limit = len(edges) + 1
        while limit > 0:
            current_poly.append(curr)
            if are_close(curr, start_edge_p1, EPSILON):
                break
                
            neighbors = graph.get(to_key(curr), [])
            next_node = None
            for n in neighbors:
                next_edge_id = (to_key(curr), to_key(n))
                if next_edge_id not in used_edges:
                    next_node = n
                    used_edges.add(next_edge_id)
                    break
            
            if next_node is None:
                break
            curr = next_node
            limit -= 1
        
        if len(current_poly) >= 3 and are_close(current_poly[0], current_poly[-1], EPSILON):
            # Remove the last point as it's the same as the first
            polygons.append(Polygon(current_poly[:-1]).cleanup())

    return polygons


__all__ = [
    "polygon_union",
    "polygon_intersection",
    "polygon_difference",
    "polygon_xor",
]
