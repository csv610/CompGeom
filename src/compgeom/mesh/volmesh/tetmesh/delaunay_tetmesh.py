"""Unified interface for Delaunay tetrahedralization algorithms."""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, Optional, List, Tuple

from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.tetmesh.tetmesh import TetMesh
from compgeom.mesh.volmesh.tetmesh.delaunay_mesh_incremental import triangulate_incremental_3d

class DelaunayTetMesher:
    """
    A unified interface for Delaunay tetrahedralization algorithms.
    """

    @staticmethod
    def triangulate(points: list[Point3D], algorithm: str = "incremental") -> TetMesh:
        """
        Performs Delaunay tetrahedralization.
        """
        if not points:
            return TetMesh([], [])

        if algorithm == "incremental":
            tets = triangulate_incremental_3d(points)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        # Convert tets (list of tuples of points) to TetMesh (indices)
        unique_points = []
        point_to_idx = {}
        
        for tet in tets:
            for p in tet:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        tet_indices = []
        for tet in tets:
            tet_indices.append((point_to_idx[tet[0]], point_to_idx[tet[1]], point_to_idx[tet[2]], point_to_idx[tet[3]]))
            
        return TetMesh(unique_points, tet_indices)

def tetmesher(points: list[Point3D], algorithm: str = "incremental") -> TetMesh:
    """Performs Delaunay tetrahedralization and returns a TetMesh object."""
    return DelaunayTetMesher.triangulate(points, algorithm)

# Alias for backward compatibility
triangulate = tetmesher

__all__ = [
    "DelaunayTetMesher",
    "tetmesher",
    "triangulate",
]
