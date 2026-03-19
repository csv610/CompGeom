from __future__ import annotations
import math
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict
from compgeom.kernel.point import Point2D
from compgeom.kernel.math_utils import EPSILON, cross_product, is_on_segment

class PlanarArrangement:
    """
    Computes and maintains a planar arrangement of line segments.
    Provides topological information about faces, edges, and vertices.
    """
    def __init__(self, segments: List[Tuple[Point2D, Point2D]]):
        self.segments = segments
        self.vertices: List[Point2D] = []
        self.edges: List[Tuple[int, int]] = []
        self.faces: List[List[Point2D]] = []
        self._compute()

    def _compute(self):
        """Computes the arrangement by splitting segments at all intersections."""
        # 1. Find all intersection points and split segments
        split_points = []
        for start, end in self.segments:
            split_points.append({self._point_key(start): start, self._point_key(end): end})

        n = len(self.segments)
        for i in range(n):
            for j in range(i + 1, n):
                intersections = self._segment_intersection_points(self.segments[i], self.segments[j])
                for pt in intersections:
                    key = self._point_key(pt)
                    split_points[i][key] = pt
                    split_points[j][key] = pt

        # 2. Build unique vertices and edges
        unique_vertices = {}
        processed_edges = set()
        
        for i, (start, end) in enumerate(self.segments):
            # Sort points along the segment
            pts = sorted(split_points[i].values(), key=lambda p: self._segment_param(p, start, end))
            
            for j in range(len(pts) - 1):
                p1, p2 = pts[j], pts[j+1]
                if p1 == p2: continue
                
                k1, k2 = self._point_key(p1), self._point_key(p2)
                if k1 not in unique_vertices: unique_vertices[k1] = p1
                if k2 not in unique_vertices: unique_vertices[k2] = p2
                
                edge = tuple(sorted((k1, k2)))
                processed_edges.add(edge)

        # Map keys to indices
        vertex_keys = sorted(unique_vertices.keys())
        key_to_idx = {k: i for i, k in enumerate(vertex_keys)}
        self.vertices = [unique_vertices[k] for k in vertex_keys]
        
        for k1, k2 in processed_edges:
            self.edges.append((key_to_idx[k1], key_to_idx[k2]))

    def _point_key(self, p: Point2D) -> Tuple[int, int]:
        return (round(p.x / 1e-9), round(p.y / 1e-9))

    def _segment_param(self, p, s, e):
        dx, dy = e.x - s.x, e.y - s.y
        if abs(dx) > abs(dy):
            return (p.x - s.x) / dx if abs(dx) > 1e-12 else 0.0
        return (p.y - s.y) / dy if abs(dy) > 1e-12 else 0.0

    def _segment_intersection_points(self, s1, s2) -> List[Point2D]:
        a, b = s1
        c, d = s2
        denom = (b.x - a.x) * (d.y - c.y) - (b.y - a.y) * (d.x - c.x)
        if abs(denom) < 1e-12:
            res = []
            for p in [a, b, c, d]:
                if is_on_segment(p, a, b) and is_on_segment(p, c, d):
                    res.append(p)
            return res
        
        t = ((c.x - a.x) * (d.y - c.y) - (c.y - a.y) * (d.x - c.x)) / denom
        u = ((c.x - a.x) * (b.y - a.y) - (c.y - a.y) * (b.x - a.x)) / denom
        
        if -1e-12 <= t <= 1 + 1e-12 and -1e-12 <= u <= 1 + 1e-12:
            return [Point2D(a.x + t * (b.x - a.x), a.y + t * (b.y - a.y))]
        return []
