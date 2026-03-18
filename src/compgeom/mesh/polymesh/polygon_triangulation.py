"""Polygon Triangulation using the Ear Clipping algorithm."""
from typing import List, Tuple
import math

from compgeom.kernel import Point2D

class PolygonTriangulation:
    """Triangulates simple 2D polygons."""

    @staticmethod
    def triangulate(polygon: List[Point2D]) -> List[Tuple[int, int, int]]:
        """
        Triangulates a simple polygon using the O(N^2) Ear Clipping method.
        Returns a list of tuples containing the indices of the vertices forming each triangle.
        Assumes the polygon is given in counter-clockwise order.
        """
        if len(polygon) < 3:
            return []
            
        # Create a working list of indices
        indices = list(range(len(polygon)))
        triangles = []
        
        def is_ear(u: int, v: int, w: int, n: int, indices: List[int]) -> bool:
            p_u, p_v, p_w = polygon[u], polygon[v], polygon[w]
            
            # Check if convex (counter-clockwise turn)
            cross = (p_v.x - p_u.x) * (p_w.y - p_u.y) - (p_v.y - p_u.y) * (p_w.x - p_u.x)
            if cross <= 1e-9:
                return False
                
            # Check if any other point is inside the triangle
            for p_idx in indices:
                if p_idx in (u, v, w): continue
                p = polygon[p_idx]
                
                # Barycentric coordinates for point-in-triangle test
                v0 = (p_w.x - p_u.x, p_w.y - p_u.y)
                v1 = (p_v.x - p_u.x, p_v.y - p_u.y)
                v2 = (p.x - p_u.x, p.y - p_u.y)
                
                dot00 = v0[0]*v0[0] + v0[1]*v0[1]
                dot01 = v0[0]*v1[0] + v0[1]*v1[1]
                dot02 = v0[0]*v2[0] + v0[1]*v2[1]
                dot11 = v1[0]*v1[0] + v1[1]*v1[1]
                dot12 = v1[0]*v2[0] + v1[1]*v2[1]
                
                invDenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
                u_bary = (dot11 * dot02 - dot01 * dot12) * invDenom
                v_bary = (dot00 * dot12 - dot01 * dot02) * invDenom
                
                if (u_bary >= 0) and (v_bary >= 0) and (u_bary + v_bary < 1):
                    return False # Point inside, not an ear
            return True

        # O(N^2) Ear Clipping
        n = len(indices)
        while n > 3:
            ear_found = False
            for i in range(n):
                u = indices[i]
                v = indices[(i+1)%n]
                w = indices[(i+2)%n]
                
                if is_ear(u, v, w, n, indices):
                    triangles.append((u, v, w))
                    indices.pop((i+1)%n)
                    ear_found = True
                    break
                    
            if not ear_found:
                # Fallback for degenerate polygons
                break
                
            n -= 1
            
        if n == 3:
            triangles.append((indices[0], indices[1], indices[2]))
            
        return triangles
