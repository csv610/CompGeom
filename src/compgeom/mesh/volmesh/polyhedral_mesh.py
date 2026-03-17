from __future__ import annotations
from typing import List, Tuple, Optional, Set
from ...kernel import Point3D
from ..mesh import Mesh

class PolyhedralMesh(Mesh):
    """
    A 3D volumetric mesh composed of arbitrary polyhedral cells.
    Each cell is defined by a list of faces.
    Each face is a list of vertex indices.
    """

    def __init__(self, 
                 vertices: List[Point3D], 
                 cells: List[List[List[int]]], 
                 seeds: Optional[List[Point3D]] = None,
                 skipped_points: Optional[List[Tuple[Point3D, str]]] = None):
        """
        Args:
            vertices: List of Point3D vertices.
            cells: List of cells. Each cell is a list of faces. 
                   Each face is a list of vertex indices (int).
            seeds: The original seed points used to generate the Voronoi mesh.
            skipped_points: Points that were not included in the mesh.
        """
        # We need to flatten the cells for the base Mesh class if it expects a specific format.
        # But our base Mesh.elements is List[Tuple[int, ...]]. 
        # For PolyhedralMesh, we'll store a more complex structure.
        # To maintain compatibility, we can store cell indices if we flatten faces.
        # For now, let's keep it simple and store our own structure.
        super().__init__(vertices, [], skipped_points)
        self._poly_cells = cells
        self._seeds = seeds or []
        self._all_faces: List[Tuple[int, ...]] = []
        self._build_faces()

    def _build_faces(self):
        """Extracts unique faces from cells."""
        unique_faces = set()
        for cell in self._poly_cells:
            for face in cell:
                # Normalize face for uniqueness
                # Sort indices but maintain winding order? 
                # Actually, for just counting unique faces, we can use frozenset or canonical rotation.
                canonical = tuple(sorted(face))
                unique_faces.add(canonical)
        # We don't really use _elements in the same way here.
        # But we'll store the poly cells directly.
        pass

    @property
    def cells(self) -> List[List[List[int]]]:
        """Returns the list of polyhedral cells."""
        return self._poly_cells

    @property
    def seeds(self) -> List[Point3D]:
        """Returns the seed points for the Voronoi cells."""
        return self._seeds

    def get_cell_faces(self, cell_idx: int) -> List[List[int]]:
        """Returns the faces of a specific cell."""
        return self._poly_cells[cell_idx]
