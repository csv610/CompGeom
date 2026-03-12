"""Unified interface for Delaunay tetrahedralization algorithms."""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, Optional, List, Tuple

from ....kernel import Point3D
from .delaunay_mesh_incremental import triangulate_incremental_3d

if TYPE_CHECKING:
    from ...mesh import TetMesh

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
            from ...mesh import TetMesh
            return TetMesh([], [])

        skipped = []

        if algorithm == "incremental":
            tets, skipped = triangulate_incremental_3d(points)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        from ...mesh import TetMesh
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
            
        return TetMesh(unique_points, tet_indices, skipped_points=skipped)

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
