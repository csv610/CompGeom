"""Voxelization utilities for 3D triangular meshes."""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np

from compgeom.kernel import Point3D
from compgeom.polygon.polygon import generate_points_in_triangle
from compgeom.mesh.surface.trimesh.trimesh import TriMesh

_THIRDPARTY_OPENVDB = Path(__file__).parents[3] / "3rdparty" / "openvdb" / "build" / "openvdb" / "openvdb"
_openvdb_dylib = _THIRDPARTY_OPENVDB / "libopenvdb.dylib"
_openvdb_so = _THIRDPARTY_OPENVDB / "libopenvdb.so"
if _openvdb_dylib.exists():
    _lib_path = str(_THIRDPARTY_OPENVDB)
    if sys.platform == "darwin":
        os.environ["DYLD_LIBRARY_PATH"] = _lib_path + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")
    else:
        os.environ["LD_LIBRARY_PATH"] = _lib_path + ":" + os.environ.get("LD_LIBRARY_PATH", "")
elif _openvdb_so.exists():
    _lib_path = str(_THIRDPARTY_OPENVDB)
    os.environ["LD_LIBRARY_PATH"] = _lib_path + ":" + os.environ.get("LD_LIBRARY_PATH", "")


class MeshVoxelizer:
    """Provides methods to voxelize 3D meshes."""

    @staticmethod
    def voxelize(mesh: TriMesh, voxel_size: float, fill_interior: bool = True) -> Set[Tuple[int, int, int]]:
        """
        Voxelizes a triangular mesh. Defaults to OpenVDB if available,
        otherwise falls back to native surface sampling.
        Returns set of voxel coordinates (i, j, k).
        """
        try:
            return MeshVoxelizer.voxelize_openvdb_to_coords(mesh, voxel_size, fill_interior=fill_interior)
        except (ImportError, RuntimeError):
            return MeshVoxelizer.voxelize_native(mesh, voxel_size, fill_interior=fill_interior)

    @staticmethod
    def voxelize_native(mesh: TriMesh, voxel_size: float, fill_interior: bool = False) -> Set[Tuple[int, int, int]]:
        """
        Voxelizes a triangular mesh using surface sampling and optional interior filling.
        Returns a set of integer voxel coordinates (ix, iy, iz).
        """
        voxels: Set[Tuple[int, int, int]] = set()
        vertices = mesh.vertices
        faces = mesh.faces

        # 1. Surface Voxelization
        for f in faces:
            v1, v2, v3 = vertices[f[0]], vertices[f[1]], vertices[f[2]]

            edge1 = math.sqrt((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2 + (v1.z - v2.z) ** 2)
            edge2 = math.sqrt((v2.x - v3.x) ** 2 + (v2.y - v3.y) ** 2 + (v2.z - v3.z) ** 2)
            edge3 = math.sqrt((v3.x - v1.x) ** 2 + (v3.y - v1.y) ** 2 + (v3.z - v1.z) ** 2)
            max_edge = max(edge1, edge2, edge3)

            n_samples = max(10, int((max_edge / voxel_size) ** 2 * 2))

            samples = generate_points_in_triangle(v1, v2, v3, n_samples)
            for p in samples:
                voxels.add(
                    (
                        int(math.floor(p.x / voxel_size)),
                        int(math.floor(p.y / voxel_size)),
                        int(math.floor(p.z / voxel_size)),
                    )
                )

        # 2. Interior Filling (Parity-based scanline)
        if fill_interior and voxels:
            min_x = min(v[0] for v in voxels)
            max_x = max(v[0] for v in voxels)
            min_y = min(v[1] for v in voxels)
            max_y = max(v[1] for v in voxels)

            interior_voxels = set()

            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    z_boundaries = sorted([v[2] for v in voxels if v[0] == x and v[1] == y])
                    if not z_boundaries:
                        continue
                    for i in range(len(z_boundaries) - 1):
                        z_start, z_end = z_boundaries[i], z_boundaries[i + 1]
                        if z_end - z_start > 1:
                            for z in range(z_start + 1, z_end):
                                interior_voxels.add((x, y, z))

            voxels.update(interior_voxels)

        return voxels

    @staticmethod
    def voxelize_openvdb(
        mesh: TriMesh,
        voxel_size: float,
        bandwidth: float = 3.0,
        fill_interior: bool = True,
    ):
        """
        Voxelizes a triangular mesh using openvdb (native Python bindings).
        Returns an openvdb.FloatGrid.
        If fill_interior is True, returns a Level Set (SDF).
        """
        try:
            import openvdb
        except ImportError:
            raise ImportError("openvdb is not installed. Please install it to use this method.")

        points = np.array([(v.x, v.y, v.z) for v in mesh.vertices], dtype=np.float32)
        triangles = np.array([tuple(f) for f in mesh.faces], dtype=np.uint32)

        transform = openvdb.createLinearTransform(voxel_size)

        grid = openvdb.FloatGrid.createLevelSetFromPolygons(
            points,
            triangles=triangles,
            transform=transform,
            halfWidth=bandwidth,
        )

        return grid

    @staticmethod
    def voxelize_openvdb_to_coords(
        mesh: TriMesh,
        voxel_size: float,
        fill_interior: bool = True,
    ) -> Set[Tuple[int, int, int]]:
        """Voxelizes a mesh using OpenVDB and returns coordinates as set of (i,j,k)."""
        try:
            import openvdb
        except ImportError:
            raise ImportError("openvdb is not installed.")

        points = np.array([(v.x, v.y, v.z) for v in mesh.vertices], dtype=np.float32)
        triangles = np.array([tuple(f) for f in mesh.faces], dtype=np.uint32)

        transform = openvdb.createLinearTransform(voxel_size)

        grid = openvdb.FloatGrid.createLevelSetFromPolygons(
            points,
            triangles=triangles,
            transform=transform,
            halfWidth=3.0,
        )

        voxels: Set[Tuple[int, int, int]] = set()
        if fill_interior:
            for it in grid.iterOnValues():
                coord_min = it.min
                coord_max = it.max
                for x in range(coord_min[0], coord_max[0] + 1):
                    for y in range(coord_min[1], coord_max[1] + 1):
                        for z in range(coord_min[2], coord_max[2] + 1):
                            voxels.add((x, y, z))
        else:
            for it in grid.iterOnValues():
                if abs(it.value) < voxel_size * 0.5:
                    coord_min = it.min
                    coord_max = it.max
                    for x in range(coord_min[0], coord_max[0] + 1):
                        for y in range(coord_min[1], coord_max[1] + 1):
                            for z in range(coord_min[2], coord_max[2] + 1):
                                voxels.add((x, y, z))

        return voxels

    @staticmethod
    def save_vdb(grid, filename: str):
        """Saves an OpenVDB grid to a file."""
        import openvdb

        if not isinstance(grid, openvdb.GridBase):
            raise ImportError("Invalid OpenVDB grid")
        openvdb.write(filename, grid)


__all__ = ["MeshVoxelizer"]
