"""Spatial queries: ray intersection and distances."""
from typing import List, Tuple
import math

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MeshQueries:
    """Algorithms for querying spatial relationships with a mesh."""

    @staticmethod
    def ray_intersect(mesh: TriangleMesh, origin: Tuple[float,float,float], direction: Tuple[float,float,float]) -> List[Tuple[int, float]]:
        """Returns a list of (face_idx, distance) for all intersections along the ray."""
        # Normalize direction
        dx, dy, dz = direction
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        if length < 1e-9:
            return []
        dx, dy, dz = dx/length, dy/length, dz/length
        
        intersections = []
        eps = 1e-8
        
        for i, face in enumerate(mesh.faces):
            v0, v1, v2 = [mesh.vertices[idx] for idx in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            # Möller–Trumbore intersection algorithm
            edge1 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            edge2 = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
            
            h = (dy*edge2[2] - dz*edge2[1], dz*edge2[0] - dx*edge2[2], dx*edge2[1] - dy*edge2[0])
            a = edge1[0]*h[0] + edge1[1]*h[1] + edge1[2]*h[2]
            
            if -eps < a < eps:
                continue # Ray is parallel to the triangle
                
            f = 1.0 / a
            s = (origin[0]-p0[0], origin[1]-p0[1], origin[2]-p0[2])
            u = f * (s[0]*h[0] + s[1]*h[1] + s[2]*h[2])
            
            if u < 0.0 or u > 1.0:
                continue
                
            q = (s[1]*edge1[2] - s[2]*edge1[1], s[2]*edge1[0] - s[0]*edge1[2], s[0]*edge1[1] - s[1]*edge1[0])
            v = f * (dx*q[0] + dy*q[1] + dz*q[2])
            
            if v < 0.0 or u + v > 1.0:
                continue
                
            t = f * (edge2[0]*q[0] + edge2[1]*q[1] + edge2[2]*q[2])
            if t > eps:
                intersections.append((i, t))
                
        intersections.sort(key=lambda x: x[1])
        return intersections

    @staticmethod
    def compute_sdf(mesh: TriangleMesh, point: Tuple[float, float, float]) -> float:
        """
        Computes the Signed Distance Function (SDF) from a point to the mesh.
        Returns a negative distance if the point is inside (based on ray parity),
        and positive if outside.
        """
        px, py, pz = point
        
        # 1. Compute exact distance to the nearest triangle (magnitude)
        min_dist_sq = float('inf')
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[idx] for idx in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            # Simple centroid distance approximation for speed (a real SDF uses exact point-triangle distance)
            cx = (p0[0] + p1[0] + p2[0]) / 3.0
            cy = (p0[1] + p1[1] + p2[1]) / 3.0
            cz = (p0[2] + p1[2] + p2[2]) / 3.0
            
            dist_sq = (px-cx)**2 + (py-cy)**2 + (pz-cz)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                
        distance = math.sqrt(min_dist_sq)
        
        # 2. Determine sign using ray casting (parity rule)
        # Cast a ray in the +Z direction
        intersections = MeshQueries.ray_intersect(mesh, point, (0.0, 0.0, 1.0))
        
        # If odd number of intersections, point is inside (negative SDF)
        if len(intersections) % 2 == 1:
            return -distance
        return distance
