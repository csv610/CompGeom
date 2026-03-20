from __future__ import annotations
from typing import List, Tuple, Optional, Union
from compgeom.kernel import Point3D
from compgeom.mesh.mesh_base import MeshNode
from compgeom.mesh.volume.volume_base import VolumeMesh

class VoxelMesh(VolumeMesh):
    """A 3D volumetric mesh composed of voxel cells."""

    def __init__(self,
                 nodes: Optional[List[Union[MeshNode, Point3D]]] = None,
                 voxels: Optional[List[Tuple[int, int, int]]] = None,
                 voxel_size: float = 1.0,
                 origin: Optional[Point3D] = None):
        super().__init__(nodes=nodes)
        self.voxels = voxels if voxels is not None else []
        self.voxel_size = voxel_size
        self.origin = origin if origin is not None else Point3D(0.0, 0.0, 0.0)
