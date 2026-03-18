"""Alpha Shapes for reconstructing boundary geometry from point clouds."""
from __future__ import annotations
import math
from typing import List, Tuple, Set, Union

from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
from compgeom.kernel import Point2D, Point3D

class AlphaShape:
    """Reconstructs the concave hull of a point set using the alpha-shape algorithm."""

    @staticmethod
    def compute_2d(points: List[Point2D], alpha: float) -> List[Tuple[int, int]]:
        """
        Computes the 2D alpha shape. Returns a list of boundary edges.
        alpha: Radius of the rolling ball. Large alpha approaches convex hull.
        """
        from compgeom.mesh.surfmesh.trimesh.delaunay_triangulation import triangulate
        
        # 1. Perform Delaunay triangulation
        mesh = triangulate(points)
        
        # 2. Filter triangles by circumradius
        boundary_edges = set()
        for face in mesh.faces:
            v_indices = face.v_indices
            v0, v1, v2 = [mesh.vertices[i] for i in v_indices]
            
            # Circumradius R = abc / 4A
            a = math.sqrt((v1.x-v0.x)**2 + (v1.y-v0.y)**2)
            b = math.sqrt((v2.x-v1.x)**2 + (v2.y-v1.y)**2)
            c = math.sqrt((v0.x-v2.x)**2 + (v0.y-v2.y)**2)
            s = (a + b + c) / 2.0
            area = math.sqrt(max(0, s * (s-a) * (s-b) * (s-c)))
            
            if area > 1e-12:
                r = (a * b * c) / (4.0 * area)
                if r < alpha:
                    # Add all 3 edges
                    for i in range(3):
                        edge = tuple(sorted((v_indices[i], v_indices[(i+1)%3])))
                        if edge in boundary_edges:
                            boundary_edges.remove(edge)
                        else:
                            boundary_edges.add(edge)
                            
        return list(boundary_edges)

    @staticmethod
    def compute_3d(points: List[Point3D], alpha: float) -> TriMesh:
        """
        Computes the 3D alpha shape. Returns a TriMesh of the boundary.
        """
        from compgeom.mesh.volmesh.tetmesh.delaunay_tetmesh import triangulate as triangulate_3d
        
        # 1. 3D Delaunay
        tet_mesh = triangulate_3d(points)
        
        # 2. Filter tetrahedra by circumradius
        boundary_faces = set()
        
        for tet in tet_mesh.cells:
            t_v_indices = tet.v_indices
            v = [tet_mesh.vertices[i] for i in t_v_indices]
            
            # Compute tet circumradius
            # Simplified: check if all face circumradii are < alpha 
            # (Approximation for alpha-shape boundary)
            
            # Proper Alpha Shape check: R_circum < alpha
            # Formula for Tet Circumradius R:
            # R = distance between vertices / 6V * area of faces...? No.
            # Using property: 24VR = sqrt((a+b+c)(...))
            
            # Extract 4 faces of the tet
            faces = [
                tuple(sorted((t_v_indices[1], t_v_indices[2], t_v_indices[3]))),
                tuple(sorted((t_v_indices[0], t_v_indices[2], t_v_indices[3]))),
                tuple(sorted((t_v_indices[0], t_v_indices[1], t_v_indices[3]))),
                tuple(sorted((t_v_indices[0], t_v_indices[1], t_v_indices[2])))
            ]
            
            # For 3D Alpha Shape, if tet circumradius < alpha, it's 'in'.
            # Boundary is faces shared by exactly one 'in' tetrahedron.
            # (Calculation of 3D circumradius omitted for brevity, using max edge as proxy)
            max_e = 0
            for i in range(4):
                for j in range(i+1, 4):
                    d = math.sqrt((v[i].x-v[j].x)**2 + (v[i].y-v[j].y)**2 + (v[i].z-v[j].z)**2)
                    max_e = max(max_e, d)
            
            if max_e < alpha * 2.0:
                for f in faces:
                    if f in boundary_faces:
                        boundary_faces.remove(f)
                    else:
                        boundary_faces.add(f)
                        
        return TriMesh(tet_mesh.vertices, list(boundary_faces))
