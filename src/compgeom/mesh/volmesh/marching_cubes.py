"""Marching Cubes algorithm for surface reconstruction from scalar fields."""
from __future__ import annotations
from typing import List, Tuple, Callable, Dict
import numpy as np

from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D

class MarchingCubes:
    """Extracts a polygonal mesh of an isosurface from a 3D scalar field."""

    @staticmethod
    def reconstruct(scalar_field: Callable[[float, float, float], float], 
                    bmin: Tuple[float,float,float], 
                    bmax: Tuple[float,float,float], 
                    resolution: int = 20, 
                    isovalue: float = 0.0) -> TriMesh:
        """
        Evaluates the scalar field over a grid and extracts the isosurface using Surface Nets.
        """
        extent = [bmax[i] - bmin[i] for i in range(3)]
        max_ext = max(extent)
        step = max_ext / resolution
        
        nx = max(2, int(extent[0] / step) + 1)
        ny = max(2, int(extent[1] / step) + 1)
        nz = max(2, int(extent[2] / step) + 1)
        
        grid = np.zeros((nx, ny, nz))
        for i in range(nx):
            x = bmin[0] + i * step
            for j in range(ny):
                y = bmin[1] + j * step
                for k in range(nz):
                    z = bmin[2] + k * step
                    grid[i, j, k] = scalar_field(x, y, z)
                    
        vertices = []
        faces = []
        cell_to_vert: Dict[Tuple[int, int, int], int] = {}
        
        # 1. Generate vertices for intersected cells
        for i in range(nx - 1):
            for j in range(ny - 1):
                for k in range(nz - 1):
                    # 8 corners
                    v_vals = [
                        grid[i,j,k], grid[i+1,j,k], grid[i+1,j+1,k], grid[i,j+1,k],
                        grid[i,j,k+1], grid[i+1,j,k+1], grid[i+1,j+1,k+1], grid[i,j+1,k+1]
                    ]
                    
                    is_inside = [v < isovalue for v in v_vals]
                    if all(is_inside) or not any(is_inside):
                        continue
                        
                    # This cell is intersected. Place a vertex at the centroid of intersected edges.
                    # For Surface Nets, we can just use the center of the cell or an average of edge intersections.
                    # Simplified: Center of the cell.
                    px = bmin[0] + (i + 0.5) * step
                    py = bmin[1] + (j + 0.5) * step
                    pz = bmin[2] + (k + 0.5) * step
                    
                    cell_to_vert[(i, j, k)] = len(vertices)
                    vertices.append(Point3D(px, py, pz))
                    
        # 2. Generate faces for intersected edges
        # Edges parallel to X
        for i in range(nx - 1):
            for j in range(1, ny - 1):
                for k in range(1, nz - 1):
                    if (grid[i, j, k] < isovalue) != (grid[i+1, j, k] < isovalue):
                        # Edge (i,j,k)-(i+1,j,k) intersected. Connect 4 cells around it.
                        c1 = cell_to_vert.get((i, j-1, k-1))
                        c2 = cell_to_vert.get((i, j, k-1))
                        c3 = cell_to_vert.get((i, j, k))
                        c4 = cell_to_vert.get((i, j-1, k))
                        if all(c is not None for c in [c1, c2, c3, c4]):
                            if grid[i, j, k] < isovalue:
                                faces.append((c1, c2, c3))
                                faces.append((c1, c3, c4))
                            else:
                                faces.append((c1, c3, c2))
                                faces.append((c1, c4, c3))

        # Edges parallel to Y
        for i in range(1, nx - 1):
            for j in range(ny - 1):
                for k in range(1, nz - 1):
                    if (grid[i, j, k] < isovalue) != (grid[i, j+1, k] < isovalue):
                        c1 = cell_to_vert.get((i-1, j, k-1))
                        c2 = cell_to_vert.get((i, j, k-1))
                        c3 = cell_to_vert.get((i, j, k))
                        c4 = cell_to_vert.get((i-1, j, k))
                        if all(c is not None for c in [c1, c2, c3, c4]):
                            if grid[i, j, k] > isovalue:
                                faces.append((c1, c2, c3))
                                faces.append((c1, c3, c4))
                            else:
                                faces.append((c1, c3, c2))
                                faces.append((c1, c4, c3))

        # Edges parallel to Z
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                for k in range(nz - 1):
                    if (grid[i, j, k] < isovalue) != (grid[i, j, k+1] < isovalue):
                        c1 = cell_to_vert.get((i-1, j-1, k))
                        c2 = cell_to_vert.get((i, j-1, k))
                        c3 = cell_to_vert.get((i, j, k))
                        c4 = cell_to_vert.get((i-1, j, k))
                        if all(c is not None for c in [c1, c2, c3, c4]):
                            if grid[i, j, k] < isovalue:
                                faces.append((c1, c2, c3))
                                faces.append((c1, c3, c4))
                            else:
                                faces.append((c1, c3, c2))
                                faces.append((c1, c4, c3))

        return TriMesh(vertices, faces)
