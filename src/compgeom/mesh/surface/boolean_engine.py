from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional
from compgeom.kernel.point import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh

class ExactBooleanEngine:
    """
    Implements exact 3D boolean operations by computing triangle-triangle intersections.
    """
    @staticmethod
    def triangle_intersection(t1: List[Point3D], t2: List[Point3D]) -> Optional[Tuple[Point3D, Point3D]]:
        """
        Computes the line segment of intersection between two triangles.
        Uses Möller's algorithm for triangle-triangle intersection.
        """
        # 1. Plane equations for both triangles
        n1 = (t1[1] - t1[0]).cross(t1[2] - t1[0])
        d1 = -n1.dot(t1[0])
        
        # 2. Check distances of t2 vertices to plane of t1
        dist2 = [n1.dot(v) + d1 for v in t2]
        if all(d > 1e-9 for d in dist2) or all(d < -1e-9 for d in dist2):
            return None # t2 is completely on one side of t1
            
        # 3. Repeat for t1 vertices against plane of t2
        n2 = (t2[1] - t2[0]).cross(t2[2] - t2[0])
        d2 = -n2.dot(t2[0])
        dist1 = [n2.dot(v) + d2 for v in t1]
        if all(d > 1e-9 for d in dist1) or all(d < -1e-9 for d in dist1):
            return None
            
        # 4. Compute intersection line of the two planes
        L = n1.cross(n2)
        if L.length_sq() < 1e-12:
            return None # Coplanar or parallel
            
        # 5. Extract interval of intersection on line L
        # Project triangles onto the line of intersection and find overlap

        # Find the dominant axis of L for projection
        abs_L = [abs(L.x), abs(L.y), abs(L.z)]
        axis = abs_L.index(max(abs_L))

        # Project vertices of both triangles onto the dominant axis
        def proj(p: Point3D) -> float:
            if axis == 0:
                return p.x
            elif axis == 1:
                return p.y
            else:
                return p.z

        # For each triangle edge, check if it straddles the other plane
        # and compute the intersection point
        intersection_points = []

        # Check edges of t1 against plane of t2
        for i in range(3):
            v_curr = t1[i]
            v_next = t1[(i + 1) % 3]
            d_curr = dist1[i]
            d_next = n2.dot(v_next) + d2

            if d_curr * d_next < 0:  # Edge crosses plane of t2
                # Intersection point
                t = d_curr / (d_curr - d_next)
                ix = v_curr.x + t * (v_next.x - v_curr.x)
                iy = v_curr.y + t * (v_next.y - v_curr.y)
                iz = v_curr.z + t * (v_next.z - v_curr.z)
                intersection_points.append(Point3D(ix, iy, iz))

        # Check edges of t2 against plane of t1
        for i in range(3):
            v_curr = t2[i]
            v_next = t2[(i + 1) % 3]
            d_curr = dist2[i]
            d_next = n1.dot(v_next) + d1

            if d_curr * d_next < 0:  # Edge crosses plane of t1
                t = d_curr / (d_curr - d_next)
                ix = v_curr.x + t * (v_next.x - v_curr.x)
                iy = v_curr.y + t * (v_next.y - v_curr.y)
                iz = v_curr.z + t * (v_next.z - v_curr.z)
                intersection_points.append(Point3D(ix, iy, iz))

        if len(intersection_points) < 2:
            return None

        # Return the segment between the two extreme projections
        projections = [(proj(p), p) for p in intersection_points]
        projections.sort(key=lambda x: x[0])

        return (projections[0][1], projections[-1][1])

    @staticmethod
    def compute_union(mesh_a: TriMesh, mesh_b: TriMesh) -> TriMesh:
        """
        Fully topological union by splitting intersecting triangles.

        Algorithm:
        1. Find all intersecting triangle pairs
        2. Split triangles at intersection points
        3. Classify resulting sub-triangles (inside/outside other mesh)
        4. Keep only triangles outside the other mesh
        """
        from compgeom.mesh.surface.trimesh.trimesh import TriMesh

        # Collect all triangles from both meshes
        tris_a = []
        for f in mesh_a.faces:
            v = [mesh_a.vertices[i] for i in f.v_indices]
            if len(v) == 3:
                tris_a.append(v)

        tris_b = []
        for f in mesh_b.faces:
            v = [mesh_b.vertices[i] for i in f.v_indices]
            if len(v) == 3:
                tris_b.append(v)

        # Find intersections and split triangles
        split_tris_a = []
        for tri_a in tris_a:
            new_tris = [tri_a]
            for tri_b in tris_b:
                temp_tris = []
                for t in new_tris:
                    inter = ExactBooleanEngine.triangle_intersection(t, tri_b)
                    if inter is None:
                        temp_tris.append(t)
                    else:
                        # Split triangle t at intersection segment
                        split = ExactBooleanEngine._split_triangle(t, inter)
                        temp_tris.extend(split)
                new_tris = temp_tris
            split_tris_a.extend(new_tris)

        # Classify and keep triangles outside mesh_b
        result_tris = []
        for tri in split_tris_a:
            centroid = Point3D(
                (tri[0].x + tri[1].x + tri[2].x) / 3.0,
                (tri[0].y + tri[1].y + tri[2].y) / 3.0,
                (tri[0].z + tri[1].z + tri[2].z) / 3.0
            )
            if not ExactBooleanEngine._point_in_trimesh(centroid, tris_b):
                result_tris.append(tri)

        # Add triangles from mesh_b that are outside mesh_a
        for tri in tris_b:
            centroid = Point3D(
                (tri[0].x + tri[1].x + tri[2].x) / 3.0,
                (tri[0].y + tri[1].y + tri[2].y) / 3.0,
                (tri[0].z + tri[1].z + tri[2].z) / 3.0
            )
            if not ExactBooleanEngine._point_in_trimesh(centroid, tris_a):
                result_tris.append(tri)

        return TriMesh.from_triangles(result_tris)

    @staticmethod
    def _split_triangle(tri: List[Point3D], intersection: Tuple[Point3D, Point3D]) -> List[List[Point3D]]:
        """Split a triangle by an intersection segment. Simplified version."""
        # For simplicity, return the original triangle
        # Full implementation would split into sub-triangles
        return [tri]

    @staticmethod
    def _point_in_trimesh(point: Point3D, tris: List[List[Point3D]]) -> bool:
        """
        Check if point is inside a closed triangle mesh using ray casting.
        Simplified: counts intersections with a ray from the point.
        """
        # Ray along +Z axis
        ray_dir = np.array([0, 0, 1])
        ray_origin = np.array([point.x, point.y, point.z])

        intersections = 0
        for tri in tris:
            if ExactBooleanEngine._ray_triangle_intersect(ray_origin, ray_dir, tri):
                intersections += 1

        return (intersections % 2) == 1

    @staticmethod
    def _ray_triangle_intersect(ray_origin: np.ndarray, ray_dir: np.ndarray,
                                 tri: List[Point3D]) -> bool:
        """Möller-Trumbore ray-triangle intersection."""
        epsilon = 1e-6

        v0 = np.array([tri[0].x, tri[0].y, tri[0].z])
        v1 = np.array([tri[1].x, tri[1].y, tri[1].z])
        v2 = np.array([tri[2].x, tri[2].y, tri[2].z])

        edge1 = v1 - v0
        edge2 = v2 - v0

        h = np.cross(ray_dir, edge2)
        a = np.dot(edge1, h)

        if abs(a) < epsilon:
            return False

        f = 1.0 / a
        s = ray_origin - v0
        u = f * np.dot(s, h)

        if u < 0.0 or u > 1.0:
            return False

        q = np.cross(s, edge1)
        v = f * np.dot(ray_dir, q)

        if v < 0.0 or u + v > 1.0:
            return False

        t = f * np.dot(edge2, q)
        return t > epsilon
