from __future__ import annotations
from typing import List, Tuple, Optional, Set, Union
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import Mesh, MeshNode
from compgeom.mesh.volmesh.volmesh_base import VolumeMesh

class PolyhedralMesh(VolumeMesh):
    """
    A 3D volumetric mesh composed of arbitrary polyhedral cells.
    Each cell is defined by a list of faces.
    Each face is a list of vertex indices.
    """

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point3D]], 
                 cells: List[List[List[int]]], 
                 seeds: Optional[List[Point3D]] = None):
        """
        Args:
            nodes: List of Point3D vertices or MeshNodes.
            cells: List of cells. Each cell is a list of faces. 
                   Each face is a list of vertex indices (int).
            seeds: The original seed points used to generate the Voronoi mesh.
        """
        from compgeom.mesh.mesh_base import MeshCell
        
        # Convert Polyhedral cell definitions to base MeshCell objects.
        # We store the unique vertices in v_indices and the face structure in attributes.
        mesh_cells = []
        for i, cell_faces in enumerate(cells):
            unique_v_indices = set()
            for face in cell_faces:
                unique_v_indices.update(face)
            
            # Create a base MeshCell, storing complex topology in attributes
            mesh_cells.append(MeshCell(
                id=i, 
                v_indices=tuple(sorted(unique_v_indices)),
                attributes={'faces': cell_faces}
            ))

        super().__init__(nodes=nodes, cells=mesh_cells)
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
        
        from compgeom.mesh.mesh_base import MeshFace
        self._faces = [MeshFace(i, f) for i, f in enumerate(unique_faces)]

    @property
    def poly_cells(self) -> List[List[List[int]]]:
        """Returns the list of polyhedral cells."""
        return self._poly_cells

    @property
    def seeds(self) -> List[Point3D]:
        """Returns the seed points for the Voronoi cells."""
        return self._seeds

    def get_cell_faces(self, cell_idx: int) -> List[List[int]]:
        """Returns the faces of a specific cell."""
        return self._poly_cells[cell_idx]
