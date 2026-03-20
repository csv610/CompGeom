"""Conforming Hexahedral Mesh Generation from Quad Surface Meshes."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

from compgeom.mesh.surface.quadmesh.quadmesh import QuadMesh
from compgeom.mesh.volume.hexmesh.hexmesh import HexMesh
from compgeom.kernel import Point3D

class ConformingHexMesher:
    """
    Generates volumetric hex meshes that conform to existing quad surface meshes.
    """

    @staticmethod
    def extrude_quad_mesh(mesh: QuadMesh, vector: Tuple[float, float, float], steps: int = 1) -> HexMesh:
        """
        Extrudes a QuadMesh along a vector to create a HexMesh.
        
        Args:
            mesh: The base QuadMesh.
            vector: The extrusion vector (total displacement).
            steps: Number of layers of hexes to create.
            
        Returns:
            A HexMesh conforming to the base mesh and its shifted copy.
        """
        if steps < 1:
            raise ValueError("Steps must be at least 1.")

        base_pts = np.array([[v.point.x, v.point.y, getattr(v.point, 'z', 0.0)] for v in mesh.nodes])
        num_base_pts = len(base_pts)
        v_extrude = np.array(vector) / float(steps)
        
        all_points = []
        # 1. Create all points layer by layer
        for i in range(steps + 1):
            layer_pts = base_pts + i * v_extrude
            for p in layer_pts:
                all_points.append(Point3D(p[0], p[1], p[2]))
                
        cells = []
        # 2. Create hexes connecting layers
        # For each quad face (v0, v1, v2, v3)
        for face in mesh.faces:
            v_idx = face.v_indices
            for i in range(steps):
                # Layer i vertices: v_idx + i * num_base_pts
                # Layer i+1 vertices: v_idx + (i+1) * num_base_pts
                
                # Standard VTK_HEXAHEDRON ordering: 
                # bottom quad (v0, v1, v2, v3) CCW, then top quad CCW
                bottom = [v + i * num_base_pts for v in v_idx]
                top = [v + (i + 1) * num_base_pts for v in v_idx]
                
                cells.append(tuple(bottom + top))
                
        return HexMesh(all_points, cells)

    @staticmethod
    def generate_shell(mesh: QuadMesh, thickness: float) -> HexMesh:
        """
        Creates a single layer of hexes by offsetting the quad mesh inward.
        The resulting hex mesh conforms exactly to the input QuadMesh on its outer boundary.
        """
        # 1. Compute vertex normals
        normals = np.zeros((len(mesh.vertices), 3))
        v_arr = np.array([[v.point.x, v.point.y, getattr(v.point, 'z', 0.0)] for v in mesh.nodes])
        
        for face in mesh.faces:
            v_idx = face.v_indices
            p = v_arr[list(v_idx)]
            # Quad normal (average of two triangles)
            n = (np.cross(p[1]-p[0], p[2]-p[0]) + np.cross(p[2]-p[0], p[3]-p[0])).astype(float)
            n /= (np.linalg.norm(n) + 1e-12)
            for idx in v_idx:
                normals[idx] += n
                
        # Normalize vertex normals
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        normals /= (norms + 1e-12)
        
        # 2. Create inner vertices
        inner_pts = v_arr - thickness * normals
        
        all_pts = []
        # Outer layer (original)
        for p in v_arr:
            all_pts.append(Point3D(p[0], p[1], p[2]))
        # Inner layer
        for p in inner_pts:
            all_pts.append(Point3D(p[0], p[1], p[2]))
            
        num_v = len(v_arr)
        cells = []
        for face in mesh.faces:
            v_idx = face.v_indices
            # Outer quad (CCW)
            outer = list(v_idx)
            # Inner quad (CCW)
            inner = [v + num_v for v in v_idx]
            
            # Hex: outer then inner
            cells.append(tuple(outer + inner))
            
        return HexMesh(all_pts, cells)
