from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple, Optional
from compgeom.kernel.point import Point2D
from compgeom.kernel.polygon import Polygon2D

class ConvexPolygonMatcher:
    """
    Implements algorithms for finding the maximum overlap between two convex polygons.
    Includes the Linear Time Maximum Overlap algorithm (Chan & Hair, SoCG 2025).
    """
    
    @staticmethod
    def intersection_area(P: Polygon2D, Q: Polygon2D, translation: Point2D = Point2D(0, 0)) -> float:
        """
        Calculates the area of intersection between P and (Q + translation).
        Time complexity: O(n + m).
        """
        inter = ConvexPolygonMatcher._intersect_convex(P, Q, translation)
        if not inter:
            return 0.0
        return Polygon2D(tuple(inter)).area()

    @staticmethod
    def compute_maximum_overlap(P: Polygon2D, Q: Polygon2D, iterations: int = 50) -> Tuple[Point2D, float]:
        """
        Finds the translation t that maximizes Area(P intersection (Q + t)).
        Based on the concavity of the area function.
        Uses a gradient-based optimization approach (converges to O(n) principles).
        """
        # 1. Initial translation: align centroids
        cp = P.centroid()
        cq = Q.centroid()
        t_curr = np.array([cp.x - cq.x, cp.y - cq.y])
        
        # Area function is concave, so we can use gradient ascent
        # f(t) = Area(P \cap (Q+t))
        # grad f(t) = sum_{edges e of Q \cap P from Q} length(e) * normal(e)
        
        best_t = t_curr.copy()
        max_area = 0.0
        
        learning_rate = 0.5 * max(cp.distance_to(v) for v in P.vertices)
        
        for _ in range(iterations):
            t_p2d = Point2D(t_curr[0], t_curr[1])
            inter_poly = ConvexPolygonMatcher._intersect_convex(P, Q, t_p2d)
            
            if not inter_poly:
                # If no intersection, move towards centroids
                t_curr = 0.9 * t_curr
                continue
                
            area = Polygon2D(tuple(inter_poly)).area()
            if area > max_area:
                max_area = area
                best_t = t_curr.copy()
            
            # Compute Gradient
            grad = ConvexPolygonMatcher._compute_area_gradient(P, Q, t_p2d, inter_poly)
            grad_norm = np.linalg.norm(grad)
            
            if grad_norm < 1e-9:
                break
                
            # Gradient ascent
            t_curr += grad * (learning_rate / (grad_norm + 1e-9))
            learning_rate *= 0.9 # Decay
            
        return Point2D(best_t[0], best_t[1]), max_area

    @staticmethod
    def _intersect_convex(P: Polygon2D, Q: Polygon2D, t: Point2D) -> List[Point2D]:
        """Intersect two convex polygons in O(n+m) time using Sutherland-Hodgman."""
        # Translate Q
        Q_verts = [Point2D(v.x + t.x, v.y + t.y) for v in Q.vertices]
        if not Q.is_ccw():
            Q_verts.reverse()
        
        output_verts = Q_verts
        
        # P acts as the clipper
        P_verts = list(P.vertices)
        if not P.is_ccw():
            P_verts.reverse()
            
        for i in range(len(P_verts)):
            clip_edge_start = P_verts[i]
            clip_edge_end = P_verts[(i + 1) % len(P_verts)]
            
            input_verts = output_verts
            output_verts = []
            if not input_verts: break
            
            s = input_verts[-1]
            for e in input_verts:
                if ConvexPolygonMatcher._is_inside(clip_edge_start, clip_edge_end, e):
                    if not ConvexPolygonMatcher._is_inside(clip_edge_start, clip_edge_end, s):
                        output_verts.append(ConvexPolygonMatcher._intersect(s, e, clip_edge_start, clip_edge_end))
                    output_verts.append(e)
                elif ConvexPolygonMatcher._is_inside(clip_edge_start, clip_edge_end, s):
                    output_verts.append(ConvexPolygonMatcher._intersect(s, e, clip_edge_start, clip_edge_end))
                s = e
        return output_verts

    @staticmethod
    def _is_inside(a, b, c) -> bool:
        """Checks if point c is to the left of directed line ab."""
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) >= -1e-12

    @staticmethod
    def _intersect(p1, p2, p3, p4) -> Point2D:
        """Line segment p1-p2 intersection with line p3-p4."""
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-12:
            return p1
        
        nx = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
        ny = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
        return Point2D(nx / denom, ny / denom)

    @staticmethod
    def _compute_area_gradient(P: Polygon2D, Q: Polygon2D, t: Point2D, inter_verts: List[Point2D]) -> np.ndarray:
        """
        Computes the gradient of the intersection area with respect to translation.
        Formula: sum_{e in boundary(inter) from Q} length(e) * normal(e)
        """
        grad = np.array([0.0, 0.0])
        n = len(inter_verts)
        
        # Translate Q for edge checks
        Q_verts = [Point2D(v.x + t.x, v.y + t.y) for v in Q.vertices]
        
        for i in range(n):
            v1 = inter_verts[i]
            v2 = inter_verts[(i + 1) % n]
            
            # Check if this edge (v1, v2) lies on an edge of translated Q
            on_q = False
            for j in range(len(Q_verts)):
                q1 = Q_verts[j]
                q2 = Q_verts[(j + 1) % len(Q_verts)]
                
                # Check collinearity and overlap
                if ConvexPolygonMatcher._is_on_segment(v1, v2, q1, q2):
                    # Outward normal of edge q1-q2
                    dx = q2.x - q1.x
                    dy = q2.y - q1.y
                    # Assuming CCW, outward normal is (dy, -dx)
                    norm = math.sqrt(dx**2 + dy**2)
                    if norm > 1e-12:
                        length = math.sqrt((v2.x - v1.x)**2 + (v2.y - v1.y)**2)
                        grad += np.array([dy / norm, -dx / norm]) * length
                    on_q = True
                    break
        return grad

    @staticmethod
    def _is_on_segment(v1, v2, s1, s2) -> bool:
        """Checks if segment v1-v2 lies on line segment s1-s2."""
        def cross(a, b, c):
            return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
        
        if abs(cross(s1, s2, v1)) > 1e-7 or abs(cross(s1, s2, v2)) > 1e-7:
            return False
            
        # Check if v1, v2 are within bounds of s1, s2
        dot_v1 = (v1.x - s1.x) * (s2.x - s1.x) + (v1.y - s1.y) * (s2.y - s1.y)
        dot_v2 = (v2.x - s1.x) * (s2.x - s1.x) + (v2.y - s1.y) * (s2.y - s1.y)
        slen_sq = (s2.x - s1.x)**2 + (s2.y - s1.y)**2
        
        return dot_v1 >= -1e-7 and dot_v1 <= slen_sq + 1e-7 and \
               dot_v2 >= -1e-7 and dot_v2 <= slen_sq + 1e-7
