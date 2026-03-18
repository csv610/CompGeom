from __future__ import annotations
from typing import List, Tuple, Optional, Set, Union
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import Mesh, MeshNode

class PolyhedralMesh(Mesh):
    """
    A 3D volumetric mesh composed of arbitrary polyhedral cells.
    Each cell is defined by a list of faces.
    Each face is a list of vertex indices.
    """

    def __init__(self, 
                 vertices: List[Union[MeshNode, Point3D]], 
                 cells: List[List[List[int]]], 
                 seeds: Optional[List[Point3D]] = None):
        """
        Args:
            vertices: List of Point3D vertices or MeshNodes.
            cells: List of cells. Each cell is a list of faces. 
                   Each face is a list of vertex indices (int).
            seeds: The original seed points used to generate the Voronoi mesh.
        """
        if vertices and not isinstance(vertices[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(vertices)]
        else:
            nodes = vertices

        super().__init__(nodes=nodes)
        self._poly_cells = cells
        self._seeds = seeds or []
        self._all_faces: List[Tuple[int, ...]] = []
        self._build_faces()

    def _build_faces(self):
        """Extracts unique faces from cells."""
        unique_faces = set()
        for cell in self._poly_cells:
            for face in cell:
                # Canonical representation for uniqueness
                canonical = tuple(sorted(face))
                unique_faces.add(canonical)
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
