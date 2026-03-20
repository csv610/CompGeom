from __future__ import annotations
from typing import List, Optional, Tuple, Union
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshCell, MeshEdge, MeshFace
from compgeom.mesh.volume.volume_base import VolumeMesh

class HexMesh(VolumeMesh):
    """A 3D volumetric mesh composed of hexahedral cells."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point3D]], 
                 cells: List[Union[MeshCell, Tuple[int, int, int, int, int, int, int, int]]], 
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None):
        super().__init__(nodes=nodes, cells=cells, edges=edges, faces=faces)
