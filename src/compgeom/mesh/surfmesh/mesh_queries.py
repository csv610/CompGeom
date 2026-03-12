"""Spatial queries: ray intersection and distances."""
from typing import List, Tuple
import math

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MeshQueries:
    """Algorithms for querying spatial relationships with a mesh."""

    @staticmethod
    def _single_ray_tri_intersect(mesh: TriangleMesh, face_idx: int, origin: Tuple[float,float,float], direction: Tuple[float,float,float]) -> Optional[float]:
        """Helper to test a single triangle for intersection."""
        face = mesh.faces[face_idx]
        v0, v1, v2 = [mesh.vertices[idx] for idx in face]
        p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
        p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
        p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
        
        # Möller–Trumbore
        eps = 1e-8
        edge1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
        edge2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
        
        dx, dy, dz = direction
        h = (dy*edge2[2] - dz*edge2[1], dz*edge2[0] - dx*edge2[2], dx*edge2[1] - dy*edge2[0])
        a = edge1[0]*h[0] + edge1[1]*h[1] + edge1[2]*h[2]
        
        if -eps < a < eps:
            return None
            
        f = 1.0 / a
        s = (origin[0]-p0[0], origin[1]-p0[1], origin[2]-p0[2])
        u = f * (s[0]*h[0] + s[1]*h[1] + s[2]*h[2])
        
        if u < 0.0 or u > 1.0:
            return None
            
        q = (s[1]*edge1[2] - s[2]*edge1[1], s[2]*edge1[0] - s[0]*edge1[2], s[0]*edge1[1] - s[1]*edge1[0])
        v = f * (dx*q[0] + dy*q[1] + dz*q[2])
        
        if v < 0.0 or u + v > 1.0:
            return None
            
        t = f * (edge2[0]*q[0] + edge2[1]*q[1] + edge2[2]*q[2])
        return t if t > eps else None

    @staticmethod
    def ray_intersect(mesh: TriangleMesh, origin: Tuple[float,float,float], direction: Tuple[float,float,float], use_spatial: bool = True) -> List[Tuple[int, float]]:
        """
        Returns a list of (face_idx, distance) for all intersections along the ray.
        Accelerated by AABBTree by default.
        """
        if use_spatial:
            from .spatial_acceleration import AABBTree
            tree = AABBTree(mesh)
            return tree.ray_intersect(origin, direction)
            
        # Brute force fallback
        intersections = []
        for i in range(len(mesh.faces)):
            t = MeshQueries._single_ray_tri_intersect(mesh, i, origin, direction)
            if t is not None:
                intersections.append((i, t))
                
        intersections.sort(key=lambda x: x[1])
        return intersections

    @staticmethod
    def compute_sdf(mesh: TriangleMesh, point: Tuple[float, float, float], use_spatial: bool = True) -> float:
        """
        Computes the Signed Distance Function (SDF) from a point to the mesh.
        """
        px, py, pz = point
        
        # 1. Distance magnitude (brute force for now, can be optimized further)
        min_dist_sq = float('inf')
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[idx] for idx in face]
            cx = (v0.x + v1.x + v2.x) / 3.0
            cy = (v0.y + v1.y + v2.y) / 3.0
            cz = (getattr(v0, 'z', 0.0) + getattr(v1, 'z', 0.0) + getattr(v2, 'z', 0.0)) / 3.0
            
            dist_sq = (px-cx)**2 + (py-cy)**2 + (pz-cz)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                
        distance = math.sqrt(min_dist_sq)
        
        # 2. Sign
        intersections = MeshQueries.ray_intersect(mesh, point, (0.0, 0.0, 1.0), use_spatial=use_spatial)
        if len(intersections) % 2 == 1:
            return -distance
        return distance
