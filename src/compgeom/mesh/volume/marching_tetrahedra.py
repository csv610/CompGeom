"""Marching Tetrahedra algorithm for surface extraction from volumetric data."""
from __future__ import annotations
from typing import List, Tuple, Callable, Dict, Union, Any
import numpy as np

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh
from compgeom.kernel import Point3D

class MarchingTetrahedra:
    """
    Extracts a surface mesh (TriMesh) of an isosurface from a tetrahedral mesh 
    or an implicit scalar field.
    """

    @staticmethod
    def from_tetmesh(mesh: TetMesh, node_values: np.ndarray, isovalue: float = 0.0) -> TriMesh:
        """
        Extracts the isosurface from an existing TetMesh given scalar values at nodes.
        
        Args:
            mesh: The input tetrahedral mesh.
            node_values: An array of scalar values for each node in the mesh.
            isovalue: The scalar value defining the surface.
            
        Returns:
            A TriMesh of the extracted isosurface.
        """
        if len(node_values) != len(mesh.nodes):
            raise ValueError("node_values must have same length as mesh nodes")

        vertices = []
        triangles = []
        edge_to_v_idx = {} # To avoid duplicate vertices on shared edges

        for cell in mesh.cells:
            # cell.v_indices is a tuple of 4 node indices
            v_indices = cell.v_indices
            vals = [node_values[idx] for idx in v_indices]
            
            # Determine intersection case (4 bits for 4 vertices)
            mask = 0
            for i in range(4):
                if vals[i] > isovalue:
                    mask |= (1 << i)
            
            # Cases:
            # 0000 (0) or 1111 (15): No intersection
            # 0001 (1), 0010 (2), 0100 (4), 1000 (8): 1 triangle (opposite vertex above)
            # 1110 (14), 1101 (13), 1011 (11), 0111 (7): 1 triangle (one vertex above)
            # 0011 (3), 0101 (5), 0110 (6), 1001 (9), 1010 (10), 1100 (12): 2 triangles (quad)
            
            # Define edges of tetrahedron: (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
            tet_edges = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
            
            def get_interp_v(i1, i2):
                idx1, idx2 = v_indices[i1], v_indices[i2]
                edge_key = tuple(sorted((idx1, idx2)))
                if edge_key in edge_to_v_idx:
                    return edge_to_v_idx[edge_key]
                
                # Linear interpolation
                node1 = mesh.nodes[idx1]
                node2 = mesh.nodes[idx2]
                p1 = node1.point
                p2 = node2.point
                val1, val2 = vals[i1], vals[i2]
                
                t = (isovalue - val1) / (val2 - val1)
                new_p = Point3D(
                    p1.x + t * (p2.x - p1.x),
                    p1.y + t * (p2.y - p1.y),
                    getattr(p1, 'z', 0.0) + t * (getattr(p2, 'z', 0.0) - getattr(p1, 'z', 0.0))
                )
                
                v_idx = len(vertices)
                vertices.append(new_p)
                edge_to_v_idx[edge_key] = v_idx
                return v_idx

            # Simplified logic for triangle generation
            # Case table for Marching Tetrahedra (standard lookup)
            if mask == 1 or mask == 14: # Vertex 0 is different
                triangles.append((get_interp_v(0,1), get_interp_v(0,2), get_interp_v(0,3)))
            elif mask == 2 or mask == 13: # Vertex 1 is different
                triangles.append((get_interp_v(1,0), get_interp_v(1,2), get_interp_v(1,3)))
            elif mask == 4 or mask == 11: # Vertex 2 is different
                triangles.append((get_interp_v(2,0), get_interp_v(2,1), get_interp_v(2,3)))
            elif mask == 8 or mask == 7: # Vertex 3 is different
                triangles.append((get_interp_v(3,0), get_interp_v(3,1), get_interp_v(3,2)))
            elif mask == 3 or mask == 12: # Vertices 0 and 1 are same
                # Quad: (0,2), (0,3), (1,3), (1,2)
                v02 = get_interp_v(0,2); v03 = get_interp_v(0,3); v13 = get_interp_v(1,3); v12 = get_interp_v(1,2)
                triangles.append((v02, v03, v13))
                triangles.append((v02, v13, v12))
            elif mask == 5 or mask == 10: # Vertices 0 and 2 are same
                # Quad: (0,1), (0,3), (2,3), (2,1)
                v01 = get_interp_v(0,1); v03 = get_interp_v(0,3); v23 = get_interp_v(2,3); v21 = get_interp_v(2,1)
                triangles.append((v01, v03, v23))
                triangles.append((v01, v23, v21))
            elif mask == 6 or mask == 9: # Vertices 1 and 2 are same
                # Quad: (1,0), (1,3), (2,3), (2,0)
                v10 = get_interp_v(1,0); v13 = get_interp_v(1,3); v23 = get_interp_v(2,3); v20 = get_interp_v(2,0)
                triangles.append((v10, v13, v23))
                triangles.append((v10, v23, v20))

        return TriMesh(vertices, triangles)

    @staticmethod
    def from_implicit(scalar_field: Callable[[float, float, float], float], 
                      bmin: Tuple[float,float,float], 
                      bmax: Tuple[float,float,float], 
                      resolution: int = 20, 
                      isovalue: float = 0.0) -> TriMesh:
        """
        Extracts the isosurface from an implicit field by subdividing a grid into tetrahedra.
        
        Args:
            scalar_field: Function (x,y,z) -> value.
            bmin, bmax: Bounding box.
            resolution: Number of cells along the longest dimension.
            isovalue: The threshold value.
            
        Returns:
            A TriMesh of the isosurface.
        """
        # 1. Create a background grid
        extent = [bmax[i] - bmin[i] for i in range(3)]
        max_ext = max(extent)
        step = max_ext / resolution
        
        nx = max(2, int(extent[0] / step) + 1)
        ny = max(2, int(extent[1] / step) + 1)
        nz = max(2, int(extent[2] / step) + 1)
        
        # 2. Evaluate field at grid vertices
        grid_nodes = []
        node_values = []
        for i in range(nx):
            x = bmin[0] + i * step
            for j in range(ny):
                y = bmin[1] + j * step
                for k in range(nz):
                    z = bmin[2] + k * step
                    grid_nodes.append(Point3D(x, y, z))
                    node_values.append(scalar_field(x, y, z))
        
        # 3. Subdivide each voxel into 5 or 6 tetrahedra
        # For simplicity, 6-tet decomposition of a cube
        cells = []
        def get_idx(i, j, k):
            return i * (ny * nz) + j * nz + k
            
        for i in range(nx - 1):
            for j in range(ny - 1):
                for k in range(nz - 1):
                    # Cube vertices
                    v0 = get_idx(i, j, k)
                    v1 = get_idx(i+1, j, k)
                    v2 = get_idx(i+1, j+1, k)
                    v3 = get_idx(i, j+1, k)
                    v4 = get_idx(i, j, k+1)
                    v5 = get_idx(i+1, j, k+1)
                    v6 = get_idx(i+1, j+1, k+1)
                    v7 = get_idx(i, j+1, k+1)
                    
                    # 6-tet decomposition
                    cells.append((v0, v1, v2, v6))
                    cells.append((v0, v2, v3, v6))
                    cells.append((v0, v4, v5, v6))
                    cells.append((v0, v5, v1, v6))
                    cells.append((v0, v7, v4, v6))
                    cells.append((v0, v3, v7, v6))
                    
        # 4. Use from_tetmesh
        tet_mesh = TetMesh(grid_nodes, cells)
        return MarchingTetrahedra.from_tetmesh(tet_mesh, np.array(node_values), isovalue)
