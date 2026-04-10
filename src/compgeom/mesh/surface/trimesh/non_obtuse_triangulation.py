"""Minimum Non-Obtuse Triangulation (CG:SHOP 2025)."""
from __future__ import annotations
import math
from typing import List, Tuple, Set, Optional

from compgeom.kernel import Point2D, distance
from compgeom.mesh.surface.trimesh.delaunay_triangulation import DelaunayMesher
from compgeom.mesh.surface.trimesh.trimesh import TriMesh

class NonObtuseTriangulator:
    """
    Refines a 2D triangulation by adding Steiner points to ensure all angles are <= 90 degrees.
    """
    def __init__(self, points: List[Point2D]):
        self.points = points

    def triangulate(self, max_steiner: int = 500) -> TriMesh:
        """
        Performs the refinement process.
        """
        # 1. Initial Delaunay Triangulation
        # We'll use the existing DelaunayMesher
        triangles = DelaunayMesher.triangulate(self.points)
        
        # Current set of points (may include Steiner points)
        curr_points = list(self.points)
        
        for _ in range(max_steiner):
            # 2. Find an obtuse triangle
            obtuse_tri = self._find_obtuse_triangle(curr_points, triangles)
            if obtuse_tri is None:
                break
                
            # 3. Resolve obtuse angle by adding a Steiner point
            # Strategy: Insert circumcenter or midpoint of the longest edge
            p_idx = obtuse_tri[0]
            p1, p2, p3 = [curr_points[idx] for idx in obtuse_tri]
            
            # Find longest edge
            d12 = distance(p1, p2)
            d23 = distance(p2, p3)
            d31 = distance(p3, p1)
            
            if d12 >= d23 and d12 >= d31:
                new_p = Point2D((p1.x + p2.x)/2, (p1.y + p2.y)/2)
            elif d23 >= d12 and d23 >= d31:
                new_p = Point2D((p2.x + p3.x)/2, (p2.y + p3.y)/2)
            else:
                new_p = Point2D((p3.x + p1.x)/2, (p3.y + p1.y)/2)
                
            curr_points.append(new_p)
            
            # 4. Re-triangulate
            triangles = DelaunayMesher.triangulate(curr_points)
            
        return triangles

    def _find_obtuse_triangle(self, points: List[Point2D], faces: TriMesh) -> Optional[Tuple[int, int, int]]:
        """Returns the first triangle found with an angle > 90 degrees."""
        for f_obj in faces.faces:
            f = f_obj.v_indices
            p1, p2, p3 = [points[idx] for idx in f]
            if self._is_obtuse(p1, p2, p3):
                return f
        return None

    def _is_obtuse(self, p1: Point2D, p2: Point2D, p3: Point2D) -> bool:
        """Checks if any angle in the triangle is > 90 degrees."""
        # Use dot product: <v1, v2> < 0 means angle > 90
        def dot(a, b, c):
            # dot product of (b-a) and (c-a)
            return (b.x - a.x) * (c.x - a.x) + (b.y - a.y) * (c.y - a.y)
            
        if dot(p1, p2, p3) < -1e-9: return True
        if dot(p2, p1, p3) < -1e-9: return True
        if dot(p3, p1, p2) < -1e-9: return True
        return False
