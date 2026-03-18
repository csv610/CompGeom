"""Geometric queries for meshes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Union

from compgeom.kernel import Point2D, Point3D

if TYPE_CHECKING:
    from compgeom.mesh.mesh_base import Mesh


class MeshGeometry:
    """Provides geometric query operations for meshes."""

    @staticmethod
    def centroid(mesh: Mesh) -> Union[Point2D, Point3D]:
        """Returns the geometric center of all nodes in the mesh."""
        nodes = mesh.nodes
        n = len(nodes)
        if n == 0:
            return Point2D(0, 0)
        
        sum_x = sum_y = sum_z = 0.0
        first_p = nodes[0].point
        is_3d = isinstance(first_p, Point3D)
        
        for node in nodes:
            p = node.point
            sum_x += p.x
            sum_y += p.y
            if is_3d:
                sum_z += getattr(p, 'z', 0.0)
        
        if is_3d:
            return Point3D(sum_x / n, sum_y / n, sum_z / n)
        return Point2D(sum_x / n, sum_y / n)

    @staticmethod
    def bounding_box(mesh: Mesh) -> Tuple:
        """Returns the axis-aligned bounding box (min_coords, max_coords)."""
        nodes = mesh.nodes
        if not nodes:
            return ()

        first_p = nodes[0].point
        is_3d = isinstance(first_p, Point3D)
        min_x = max_x = first_p.x
        min_y = max_y = first_p.y
        min_z = max_z = getattr(first_p, 'z', 0.0) if is_3d else 0.0

        for node in nodes[1:]:
            p = node.point
            if p.x < min_x: min_x = p.x
            elif p.x > max_x: max_x = p.x
            if p.y < min_y: min_y = p.y
            elif p.y > max_y: max_y = p.y
            if is_3d:
                vz = getattr(p, 'z', 0.0)
                if vz < min_z: min_z = vz
                elif vz > max_z: max_z = vz

        if is_3d:
            return (min_x, min_y, min_z), (max_x, max_y, max_z)
        
        return (min_x, min_y), (max_x, max_y)
