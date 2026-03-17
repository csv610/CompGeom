"""Convex Hull generation for 3D point sets."""
from typing import List

from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
from ...kernel import Point3D

class ConvexHull3D:
    """Generates the 3D Convex Hull of a point cloud."""

    @staticmethod
    def compute(points: List[Point3D]) -> TriMesh:
        """
        Computes the 3D convex hull using scipy.spatial.ConvexHull.
        Returns a TriMesh representing the boundary of the hull.
        """
        try:
            from scipy.spatial import ConvexHull
            import numpy as np
        except ImportError:
            raise ImportError("3D Convex Hull requires 'scipy' and 'numpy'.")

        if len(points) < 4:
            raise ValueError("At least 4 points are required for a 3D convex hull.")

        pts_array = np.array([[p.x, p.y, getattr(p, 'z', 0.0)] for p in points])
        
        # Compute the hull
        hull = ConvexHull(pts_array)
        
        # The vertices of the hull
        hull_vertices = []
        old_to_new = {}
        
        for i, v_idx in enumerate(hull.vertices):
            p = points[v_idx]
            hull_vertices.append(Point3D(p.x, p.y, getattr(p, 'z', 0.0)))
            old_to_new[v_idx] = i
            
        # The faces of the hull
        faces = []
        for simplex in hull.simplices:
            # Scipy ConvexHull simplices are oriented outward
            faces.append((old_to_new[simplex[0]], old_to_new[simplex[1]], old_to_new[simplex[2]]))
            
        return TriMesh(hull_vertices, faces)
