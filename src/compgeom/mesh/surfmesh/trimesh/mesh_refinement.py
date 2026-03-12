"""Refinement and subdivision algorithms for meshes."""

from __future__ import annotations

import heapq
import math
from typing import Dict, List, Optional, Set, Tuple, Union

from ....kernel import Point, Point3D
from ...mesh import TriangleMesh


class TriMeshRefiner:
    """Provides methods for refining and subdividing triangular meshes."""

    @staticmethod
    def _calculate_face_area(v0: Union[Point, Point3D], v1: Union[Point, Point3D], v2: Union[Point, Point3D]) -> float:
        """Calculates the area of a 2D or 3D triangle."""
        ax, ay, az = v0.x, v0.y, getattr(v0, 'z', 0.0)
        bx, by, bz = v1.x, v1.y, getattr(v1, 'z', 0.0)
        cx, cy, cz = v2.x, v2.y, getattr(v2, 'z', 0.0)
        
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        
        cp_x = uy * vz - uz * vy
        cp_y = uz * vx - ux * vz
        cp_z = ux * vy - uy * vx
        
        return 0.5 * math.sqrt(cp_x**2 + cp_y**2 + cp_z**2)

    @staticmethod
    def subdivide_linear(mesh: TriangleMesh) -> TriangleMesh:
        """
        Refines the mesh by splitting each triangle into 4 smaller triangles.
        New vertices are placed exactly at the midpoints of the original edges.
        """
        old_vertices = mesh.vertices
        old_faces = mesh.faces
        new_faces = []
        
        midpoints: Dict[Tuple[int, int], int] = {}
        new_vertices = list(old_vertices)

        def get_midpoint(i1: int, i2: int) -> int:
            edge = tuple(sorted((i1, i2)))
            if edge in midpoints:
                return midpoints[edge]
            
            v1, v2 = old_vertices[i1], old_vertices[i2]
            idx = len(new_vertices)
            
            if isinstance(v1, Point3D) and isinstance(v2, Point3D):
                mid = Point3D((v1.x+v2.x)/2, (v1.y+v2.y)/2, (v1.z+v2.z)/2, idx)
            else:
                mid = Point((v1.x+v2.x)/2, (v1.y+v2.y)/2, idx)
                
            new_vertices.append(mid)
            midpoints[edge] = idx
            return idx

        for face in old_faces:
            v0, v1, v2 = face
            m01 = get_midpoint(v0, v1)
            m12 = get_midpoint(v1, v2)
            m20 = get_midpoint(v2, v0)
            
            new_faces.append((v0, m01, m20))
            new_faces.append((v1, m12, m01))
            new_faces.append((v2, m20, m12))
            new_faces.append((m01, m12, m20))
            
        return TriangleMesh(new_vertices, new_faces)

    @staticmethod
    def refine_uniform(mesh: TriangleMesh, max_area_ratio: float) -> TriangleMesh:
        """
        Refines the mesh iteratively by splitting the largest triangles until 
        all triangles have an area less than (total_mesh_area * max_area_ratio).
        """
        vertices = list(mesh.vertices)
        faces = list(mesh.faces)

        # 1. Calculate total area
        total_area = sum(TriMeshRefiner._calculate_face_area(vertices[f[0]], vertices[f[1]], vertices[f[2]]) for f in faces)
        threshold_area = total_area * max_area_ratio

        # Priority queue of (-area, face_tuple)
        pq = [(-TriMeshRefiner._calculate_face_area(vertices[f[0]], vertices[f[1]], vertices[f[2]]), f) for f in faces]
        heapq.heapify(pq)

        midpoints: Dict[Tuple[int, int], int] = {}

        def get_midpoint(i1: int, i2: int) -> int:
            edge = tuple(sorted((i1, i2)))
            if edge in midpoints:
                return midpoints[edge]
            
            v1, v2 = vertices[i1], vertices[i2]
            idx = len(vertices)
            
            if isinstance(v1, Point3D) and isinstance(v2, Point3D):
                mid = Point3D((v1.x+v2.x)/2, (v1.y+v2.y)/2, (v1.z+v2.z)/2, idx)
            else:
                mid = Point((v1.x+v2.x)/2, (v1.y+v2.y)/2, idx)
                
            vertices.append(mid)
            midpoints[edge] = idx
            return idx

        while pq and -pq[0][0] > threshold_area:
            neg_area, face = heapq.heappop(pq)
            v0, v1, v2 = face
            
            m01 = get_midpoint(v0, v1)
            m12 = get_midpoint(v1, v2)
            m20 = get_midpoint(v2, v0)
            
            new_sub_faces = [
                (v0, m01, m20),
                (v1, m12, m01),
                (v2, m20, m12),
                (m01, m12, m20)
            ]
            
            for nf in new_sub_faces:
                f_area = TriMeshRefiner._calculate_face_area(vertices[nf[0]], vertices[nf[1]], vertices[nf[2]])
                heapq.heappush(pq, (-f_area, nf))

        final_faces = [f for _, f in pq]
        return TriangleMesh(vertices, final_faces)


__all__ = ["TriMeshRefiner"]
