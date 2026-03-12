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
    def _point_triangle_dist_sq(p: Tuple[float, float, float], v0: Tuple[float, float, float], 
                               v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
        """Calculates exact squared distance from a point to a triangle."""
        # Implementation of point-triangle distance in 3D
        # See Real-Time Collision Detection by Christer Ericson
        a, b, c = v0, v1, v2
        ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
        ac = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
        ap = (p[0]-a[0], p[1]-a[1], p[2]-a[2])
        
        d1 = ab[0]*ap[0] + ab[1]*ap[1] + ab[2]*ap[2]
        d2 = ac[0]*ap[0] + ac[1]*ap[1] + ac[2]*ap[2]
        if d1 <= 0 and d2 <= 0: return ap[0]**2 + ap[1]**2 + ap[2]**2
        
        bp = (p[0]-b[0], p[1]-b[1], p[2]-b[2])
        d3 = ab[0]*bp[0] + ab[1]*bp[1] + ab[2]*bp[2]
        d4 = ac[0]*bp[0] + ac[1]*bp[1] + ac[2]*bp[2]
        if d3 >= 0 and d4 <= d3: return bp[0]**2 + bp[1]**2 + bp[2]**2
        
        vc = d1*d4 - d3*d2
        if vc <= 0 and d1 >= 0 and d3 <= 0:
            v = d1 / (d1 - d3)
            return (ap[0] - v*ab[0])**2 + (ap[1] - v*ab[1])**2 + (ap[2] - v*ab[2])**2
            
        cp = (p[0]-c[0], p[1]-c[1], p[2]-c[2])
        d5 = ab[0]*cp[0] + ab[1]*cp[1] + ab[2]*cp[2]
        d6 = ac[0]*cp[0] + ac[1]*cp[1] + ac[2]*cp[2]
        if d6 >= 0 and d5 <= d6: return cp[0]**2 + cp[1]**2 + cp[2]**2
        
        vb = d5*d2 - d1*d6
        if vb <= 0 and d2 >= 0 and d6 <= 0:
            w = d2 / (d2 - d6)
            return (ap[0] - w*ac[0])**2 + (ap[1] - w*ac[1])**2 + (ap[2] - w*ac[2])**2
            
        va = d3*d6 - d5*d4
        if va <= 0 and (d4 - d3) >= 0 and (d5 - d6) >= 0:
            w = (d4 - d3) / ((d4 - d3) + (d5 - d6))
            edge = (c[0]-b[0], c[1]-b[1], c[2]-b[2])
            return (bp[0] - w*edge[0])**2 + (bp[1] - w*edge[1])**2 + (bp[2] - w*edge[2])**2
            
        denom = 1.0 / (va + vb + vc)
        v = vb * denom
        w = vc * denom
        return (ap[0] - v*ab[0] - w*ac[0])**2 + (ap[1] - v*ab[1] - w*ac[1])**2 + (ap[2] - v*ab[2] - w*ac[2])**2

    @staticmethod
    def compute_sdf(mesh: TriangleMesh, point: Tuple[float, float, float], use_spatial: bool = True) -> float:
        """
        Computes the Signed Distance Function (SDF) from a point to the mesh.
        Using exact point-triangle distance.
        """
        px, py, pz = point
        min_dist_sq = float('inf')
        
        # In a full implementation, we would use the AABBTree to narrow down candidate triangles
        # for exact distance. For now, we perform a brute force exact calculation.
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[idx] for idx in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            d_sq = MeshQueries._point_triangle_dist_sq(point, p0, p1, p2)
            if d_sq < min_dist_sq:
                min_dist_sq = d_sq
                
        distance = math.sqrt(min_dist_sq)
        
        # Sign using ray parity
        intersections = MeshQueries.ray_intersect(mesh, point, (0.0, 0.0, 1.0), use_spatial=use_spatial)
        if len(intersections) % 2 == 1:
            return -distance
        return distance
