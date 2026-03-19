from __future__ import annotations
from typing import List, Union, Optional
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshCell, MeshEdge, MeshFace

class VolumeMesh(Mesh):
    """Base class for 3D volumetric meshes."""
    
    def __init__(self, 
                 nodes: List[Union[MeshNode, Point3D]], 
                 cells: Optional[List[Union[MeshCell, Tuple[int, ...]]]] = None,
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None):
        if cells and not isinstance(cells[0], MeshCell):
            cells = [MeshCell(i, c) for i, c in enumerate(cells)]
        super().__init__(nodes=nodes, edges=edges, faces=faces, cells=cells)

