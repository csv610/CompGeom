from __future__ import annotations
from typing import List, Optional, Tuple, Union
from ....kernel import Point3D
from ...mesh_base import Mesh, MeshNode, MeshCell, MeshEdge, MeshFace

class TetMesh(Mesh):
    """A 3D volumetric mesh composed of tetrahedral cells."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point3D]], 
                 cells: List[Union[MeshCell, Tuple[int, int, int, int]]], 
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if cells and not isinstance(cells[0], MeshCell):
            cells = [MeshCell(i, c) for i, c in enumerate(cells)]
        super().__init__(nodes=nodes, cells=cells, edges=edges, faces=faces)
