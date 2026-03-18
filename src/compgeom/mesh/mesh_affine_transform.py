"""Affine transformations for meshes."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, List, Union

from compgeom.kernel import Point2D, Point3D

if TYPE_CHECKING:
    from compgeom.mesh.mesh_base import Mesh, MeshNode


class MeshAffineTransform:
    """Provides affine transformation operations for meshes."""

    @staticmethod
    def translate(mesh: Mesh, dx: float, dy: float, dz: float = 0.0):
        """Translates all nodes in the mesh by (dx, dy, dz)."""
        from compgeom.mesh.mesh_topology import MeshTopology
        
        new_nodes: List[MeshNode] = []
        for node in mesh.nodes:
            p = node.point
            if isinstance(p, Point3D):
                new_p = Point3D(p.x + dx, p.y + dy, p.z + dz, getattr(p, 'id', -1))
            else:
                new_p = Point2D(p.x + dx, p.y + dy, getattr(p, 'id', -1))
            new_nodes.append(replace(node, point=new_p))
        
        # We need to access protected members to update the mesh state
        mesh._nodes = new_nodes
        mesh._topology = MeshTopology(mesh)

    @staticmethod
    def scale(mesh: Mesh, sx: float, sy: float, sz: float = 1.0):
        """Scales all nodes in the mesh by (sx, sy, sz)."""
        from compgeom.mesh.mesh_topology import MeshTopology
        
        new_nodes = []
        for node in mesh.nodes:
            p = node.point
            if isinstance(p, Point3D):
                new_p = Point3D(p.x * sx, p.y * sy, p.z * sz, getattr(p, 'id', -1))
            else:
                new_p = Point2D(p.x * sx, p.y * sy, getattr(p, 'id', -1))
            new_nodes.append(replace(node, point=new_p))
        mesh._nodes = new_nodes
        mesh._topology = MeshTopology(mesh)

    @staticmethod
    def rotate(mesh: Mesh, angle_deg: float, axis: str = 'z'):
        """Rotates the mesh around an axis ('x', 'y', or 'z') by given degrees."""
        import math
        from compgeom.mesh.mesh_topology import MeshTopology
        
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        new_nodes = []
        for node in mesh.nodes:
            p = node.point
            x, y = p.x, p.y
            z = getattr(p, 'z', 0.0)
            is_3d = isinstance(p, Point3D)
            
            if axis.lower() == 'x' and is_3d:
                ny = y * cos_a - z * sin_a
                nz = y * sin_a + z * cos_a
                new_p = Point3D(x, ny, nz, getattr(p, 'id', -1))
            elif axis.lower() == 'y' and is_3d:
                nx = x * cos_a + z * sin_a
                nz = -x * sin_a + z * cos_a
                new_p = Point3D(nx, y, nz, getattr(p, 'id', -1))
            else: # Default Z axis
                nx = x * cos_a - y * sin_a
                ny = x * sin_a + y * cos_a
                if is_3d:
                    new_p = Point3D(nx, ny, z, getattr(p, 'id', -1))
                else:
                    new_p = Point2D(nx, ny, getattr(p, 'id', -1))
            new_nodes.append(replace(node, point=new_p))
        mesh._nodes = new_nodes
        mesh._topology = MeshTopology(mesh)

    @staticmethod
    def normalize(mesh: Mesh):
        """Centers the mesh at the origin and scales it to fit within a unit cube [-1, 1]."""
        from compgeom.mesh.mesh_geometry import MeshGeometry
        bbox = MeshGeometry.bounding_box(mesh)
        if not bbox: return
        
        (min_x, min_y, *min_z), (max_x, max_y, *max_z) = bbox
        min_z = min_z[0] if min_z else 0.0
        max_z = max_z[0] if max_z else 0.0
        
        # Center
        cx, cy, cz = (min_x + max_x)/2, (min_y + max_y)/2, (min_z + max_z)/2
        MeshAffineTransform.translate(mesh, -cx, -cy, -cz)
        
        # Scale
        dx, dy, dz = max_x - min_x, max_y - min_y, max_z - min_z
        max_dim = max(dx, dy, dz, 1e-9)
        s = 2.0 / max_dim
        MeshAffineTransform.scale(mesh, s, s, s)
