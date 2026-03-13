"""Polygon simplification and self-intersection resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Set, Dict, Tuple
from collections import defaultdict

if TYPE_CHECKING:
    from .polygon import Polygon

from ..kernel import Point2D, cross_product, distance
from .line_segment import proper_segment_intersection
from .polygon_utils import same_point, cleanup_polygon


def _intersect_segments(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Point2D | None:
    """Return the intersection point of two segments, if it exists."""
    # Using the line intersection formula and checking if it's on both segments
    denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if abs(denom) < 1e-12:
        return None

    px = (
        (p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x)
        - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)
    ) / denom
    py = (
        (p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y)
        - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)
    ) / denom
    
    intersect = Point2D(px, py)
    
    # Check if point is on both segments
    def on_segment(p: Point2D, a: Point2D, b: Point2D) -> bool:
        return (min(a.x, b.x) - 1e-9 <= p.x <= max(a.x, b.x) + 1e-9 and
                min(a.y, b.y) - 1e-9 <= p.y <= max(a.y, b.y) + 1e-9)
                
    if on_segment(intersect, p1, p2) and on_segment(intersect, p3, p4):
        return intersect
    return None

def resolve_self_intersections(polygon: Polygon) -> list[Point2D]:
    """
    Resolves self-intersections in a polygon by splitting segments at intersection
    points and returning a simple boundary. 
    
    This implementation uses a simple heuristic: it builds a graph of all 
    non-intersecting sub-segments and then extracts the largest cycle 
    (the outer boundary).
    
    Note: This is a complex problem and this implementation focuses on 
    common self-intersection cases (like a figure-8).
    """
    vertices = list(polygon.vertices)
    n = len(vertices)
    if n < 3:
        return vertices

    # 1. Find all intersection points
    edges = []
    for i in range(n):
        edges.append((vertices[i], vertices[(i + 1) % n]))

    # We will subdivide each edge by all intersection points found on it
    edge_points = defaultdict(list)
    for i in range(n):
        edge_points[i].append(edges[i][0])
        edge_points[i].append(edges[i][1])

    for i in range(n):
        for j in range(i + 1, n):
            # Skip adjacent edges
            if j == i or j == (i + 1) % n or i == (j + 1) % n:
                continue
                
            p = _intersect_segments(edges[i][0], edges[i][1], edges[j][0], edges[j][1])
            if p:
                edge_points[i].append(p)
                edge_points[j].append(p)

    # 2. Build the graph of sub-segments
    graph = defaultdict(list)
    
    def get_key(p: Point2D) -> tuple[float, float]:
        return (round(p.x, 9), round(p.y, 9))

    for i in range(n):
        # Sort points along the edge to create sub-segments
        pts = edge_points[i]
        start_pt = edges[i][0]
        # Sort by distance from start_pt
        pts.sort(key=lambda p: (p.x - start_pt.x)**2 + (p.y - start_pt.y)**2)
        
        # Remove duplicates
        unique_pts = []
        for p in pts:
            if not unique_pts or not same_point(p, unique_pts[-1]):
                unique_pts.append(p)
        
        for j in range(len(unique_pts) - 1):
            p1, p2 = unique_pts[j], unique_pts[j+1]
            if same_point(p1, p2): continue
            graph[get_key(p1)].append(p2)
            graph[get_key(p2)].append(p1)

    # 3. Traverse to find the outer boundary
    # Heuristic: Start at the leftmost-bottommost point and always take the 
    # "most external" turn.
    all_points = []
    for pts in edge_points.values():
        all_points.extend(pts)
    
    if not all_points:
        return vertices
        
    start_node = min(all_points, key=lambda p: (p.x, p.y))
    
    curr = start_node
    prev = Point2D(curr.x, curr.y - 1.0) # Virtual point to start the "turn" calculation
    
    result = []
    visited_edges = set()
    
    # Simple "Keep Right" traversal to find the outer boundary
    for _ in range(len(all_points) * 2): # Safety limit
        result.append(curr)
        neighbors = graph[get_key(curr)]
        
        if not neighbors:
            break
            
        # Find the neighbor that makes the widest right turn
        def get_angle(p: Point2D, center: Point2D, reference: Point2D) -> float:
            import math
            v1 = (reference.x - center.x, reference.y - center.y)
            v2 = (p.x - center.x, p.y - center.y)
            a1 = math.atan2(v1[1], v1[0])
            a2 = math.atan2(v2[1], v2[0])
            angle = a2 - a1
            while angle <= 0: angle += 2 * math.pi
            return angle

        # We want the smallest angle (tightest right turn)
        next_node = min(neighbors, key=lambda p: get_angle(p, curr, prev) if not same_point(p, prev) else float('inf'))
        
        edge_id = tuple(sorted([get_key(curr), get_key(next_node)]))
        if edge_id in visited_edges:
            # We hit a loop, might be done or stuck
            break
        visited_edges.add(edge_id)
        
        prev = curr
        curr = next_node
        
        if same_point(curr, start_node):
            break

    return cleanup_polygon(result)
