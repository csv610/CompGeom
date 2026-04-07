from __future__ import annotations
from typing import List, Optional, Tuple, Union
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshCell, MeshEdge, MeshFace
from compgeom.mesh.volume.volume_base import VolumeMesh


class HexMesh(VolumeMesh):
    """A 3D volumetric mesh composed of hexahedral cells."""

    def __init__(
        self,
        nodes: List[Union[MeshNode, Point3D]],
        cells: List[Union[MeshCell, Tuple[int, int, int, int, int, int, int, int]]],
        edges: Optional[List[MeshEdge]] = None,
        faces: Optional[List[MeshFace]] = None,
    ):
        super().__init__(nodes=nodes, cells=cells, edges=edges, faces=faces)

    @classmethod
    def create_structured_mesh(
        cls,
        nx: int,
        ny: int,
        nz: int,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        origin_z: float = 0.0,
        spacing: float = 1.0,
    ) -> "HexMesh":
        """Creates a 3D structured hexahedral grid.

        Args:
            nx: Number of cells in X direction.
            ny: Number of cells in Y direction.
            nz: Number of cells in Z direction.
            origin_x: Origin X coordinate.
            origin_y: Origin Y coordinate.
            origin_z: Origin Z coordinate.
            spacing: Cell spacing.

        Returns:
            A new HexMesh with structured hexahedral cells.
        """
        vertices = []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    vertices.append(Point3D(origin_x + i * spacing, origin_y + j * spacing, origin_z + k * spacing))

        cells = []
        for k in range(nz - 1):
            for j in range(ny - 1):
                for i in range(nx - 1):
                    v0 = k * ny * nx + j * nx + i
                    v1 = k * ny * nx + j * nx + (i + 1)
                    v2 = k * ny * nx + (j + 1) * nx + (i + 1)
                    v3 = k * ny * nx + (j + 1) * nx + i
                    v4 = (k + 1) * ny * nx + j * nx + i
                    v5 = (k + 1) * ny * nx + j * nx + (i + 1)
                    v6 = (k + 1) * ny * nx + (j + 1) * nx + (i + 1)
                    v7 = (k + 1) * ny * nx + (j + 1) * nx + i
                    cells.append((v0, v1, v2, v3, v4, v5, v6, v7))

        return cls(nodes=vertices, cells=cells)
