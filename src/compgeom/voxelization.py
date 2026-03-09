"""Voxelization utilities for 3D triangular meshes."""

from __future__ import annotations

import math
from typing import List, Optional, Set, Tuple, Union

from .geometry import Point3D
from .polygon import generate_points_in_triangle
from .spatial import PointSimplifier


class MeshVoxelizer:
    """Provides methods to voxelize 3D meshes."""

    @staticmethod
    def voxelize_native(
        vertices: List[Point3D], 
        faces: List[Tuple[int, int, int]], 
        voxel_size: float
    ) -> Set[Tuple[int, int, int]]:
        """
        Voxelizes a mesh using surface sampling.
        Returns a set of integer voxel coordinates (ix, iy, iz).
        """
        voxels: Set[Tuple[int, int, int]] = set()
        
        for f in faces:
            v1, v2, v3 = vertices[f[0]], vertices[f[1]], vertices[f[2]]
            
            # Heuristic: sample points based on triangle size
            edge1 = math.sqrt((v1.x-v2.x)**2 + (v1.y-v2.y)**2 + (v1.z-v2.z)**2)
            edge2 = math.sqrt((v2.x-v3.x)**2 + (v2.y-v3.y)**2 + (v2.z-v3.z)**2)
            edge3 = math.sqrt((v3.x-v1.x)**2 + (v3.y-v1.y)**2 + (v3.z-v1.z)**2)
            max_edge = max(edge1, edge2, edge3)
            
            # Number of samples proportional to triangle area/size relative to voxel size
            # Area ~ 0.5 * base * height. For simplicity, use max_edge.
            n_samples = max(10, int((max_edge / voxel_size) ** 2 * 2))
            
            samples = generate_points_in_triangle(v1, v2, v3, n_samples)
            for p in samples:
                voxels.add((
                    int(math.floor(p.x / voxel_size)),
                    int(math.floor(p.y / voxel_size)),
                    int(math.floor(p.z / voxel_size))
                ))
                
        return voxels

    @staticmethod
    def voxelize_openvdb(
        vertices: List[Point3D], 
        faces: List[Tuple[int, int, int]], 
        voxel_size: float,
        bandwidth: float = 3.0
    ):
        """
        Voxelizes a mesh using pyopenvdb (OpenVDB).
        Returns an openvdb.FloatGrid (Level Set).
        Note: Requires pyopenvdb to be installed.
        """
        try:
            import pyopenvdb as vdb
        except ImportError:
            raise ImportError("pyopenvdb is not installed. Please install it to use this method.")

        # Convert Point3D to raw list of tuples for OpenVDB
        v_list = [(v.x, v.y, v.z) for v in vertices]
        # OpenVDB meshToLevelSet expects faces as a flat list or list of tuples
        
        # Create a level set grid
        # The scale determines the voxel size
        grid = vdb.FloatGrid.meshToLevelSet(v_list, faces, exBandWidth=bandwidth, inBandWidth=bandwidth)
        grid.transform = vdb.createLinearTransform(voxel_size)
        
        return grid

    @staticmethod
    def save_vdb(grid, filename: str):
        """Saves an OpenVDB grid to a file."""
        import pyopenvdb as vdb
        vdb.write(filename, [grid])


__all__ = ["MeshVoxelizer"]
