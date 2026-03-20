"""
Maximum Overlap of Two Convex Polygons under Translation.
Inspired by Chan and Hair (SoCG 2025).
"""
from __future__ import annotations
import numpy as np
import math
from typing import List, Tuple, Optional

from compgeom.kernel import Point2D
from compgeom.polygon.convex_intersection import ConvexIntersection
from compgeom.polygon.hierarchical_polygon import HierarchicalPolygon

class MaximumOverlap:
    """
    Finds the translation vector t that maximizes the area of P intersect (Q + t).
    Uses a randomized cascading approach for O(n+m) expected performance.
    """

    @staticmethod
    def solve(poly_p: List[Point2D], poly_q: List[Point2D]) -> Tuple[Point2D, float]:
        """
        Main solver.
        
        Returns:
            A tuple (best_translation, max_area).
        """
        # 1. Build hierarchies
        hp = HierarchicalPolygon(poly_p)
        hq = HierarchicalPolygon(poly_q)
        
        # 2. Initial guess (centroid alignment)
        def get_centroid(p):
            return Point2D(sum(v.x for v in p)/len(p), sum(v.y for v in p)/len(p))
        
        cp = get_centroid(poly_p)
        cq = get_centroid(poly_q)
        t_curr = Point2D(cp.x - cq.x, cp.y - cq.y)
        
        # 3. Cascading refinement
        num_levels = max(hp.num_levels, hq.num_levels)
        
        # Search radius in translation space
        bbox_p = MaximumOverlap._get_bbox(poly_p)
        bbox_q = MaximumOverlap._get_bbox(poly_q)
        search_radius = max(bbox_p[2]-bbox_p[0], bbox_p[3]-bbox_p[1]) * 0.5
        
        best_t = t_curr
        max_area = 0.0
        
        for level in range(num_levels):
            curr_p = hp.get_level(level)
            curr_q = hq.get_level(level)
            
            # Refine t at this level using randomized search
            best_t, max_area = MaximumOverlap._randomized_search(
                curr_p, curr_q, best_t, search_radius, num_iters=20
            )
            
            # Shrink search radius for the next (finer) level
            search_radius *= 0.5
            
        return best_t, max_area

    @staticmethod
    def _randomized_search(p: List[Point2D], q: List[Point2D], 
                           t_start: Point2D, radius: float, 
                           num_iters: int) -> Tuple[Point2D, float]:
        """Performs a localized randomized search around t_start."""
        def area_at(t):
            q_shifted = [Point2D(v.x + t.x, v.y + t.y) for v in q]
            return ConvexIntersection.area(p, q_shifted)

        curr_t = t_start
        curr_area = area_at(curr_t)
        
        for _ in range(num_iters):
            # Sample multiple candidates around curr_t
            found_better = False
            for _ in range(5): # Constant number of samples per iteration
                angle = np.random.uniform(0, 2 * math.pi)
                dist = np.random.uniform(0, radius)
                t_cand = Point2D(curr_t.x + dist * math.cos(angle), 
                                 curr_t.y + dist * math.sin(angle))
                
                a = area_at(t_cand)
                if a > curr_area:
                    curr_area = a
                    curr_t = t_cand
                    found_better = True
            
            if not found_better:
                # If no improvement, reduce radius slightly and continue
                radius *= 0.7
            
        return curr_t, curr_area

    @staticmethod
    def _get_bbox(poly: List[Point2D]) -> Tuple[float, float, float, float]:
        xs = [p.x for p in poly]
        ys = [p.y for p in poly]
        return min(xs), min(ys), max(xs), max(ys)
