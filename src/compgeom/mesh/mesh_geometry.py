"""Geometric queries for meshes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Union, List

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh_base import Mesh
from compgeom.kernel.triangle import Triangle3D
from compgeom.kernel.tetrahedron import volume as tet_volume


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
                sum_z += getattr(p, "z", 0.0)

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
        min_z = max_z = getattr(first_p, "z", 0.0) if is_3d else 0.0

        for node in nodes[1:]:
            p = node.point
            if p.x < min_x:
                min_x = p.x
            elif p.x > max_x:
                max_x = p.x
            if p.y < min_y:
                min_y = p.y
            elif p.y > max_y:
                max_y = p.y
            if is_3d:
                vz = getattr(p, "z", 0.0)
                if vz < min_z:
                    min_z = vz
                elif vz > max_z:
                    max_z = vz

        if is_3d:
            return (min_x, min_y, min_z), (max_x, max_y, max_z)

        return (min_x, min_y), (max_x, max_y)

    @staticmethod
    def surface_area(mesh: Mesh) -> float:
        """Calculates the total surface area of the mesh faces."""
        total_area = 0.0
        vertices = mesh.vertices
        is_3d = isinstance(vertices[0], Point3D) if vertices else False

        for face in mesh.faces:
            if len(face) < 3:
                continue

            # Triangulate polygons if necessary
            for i in range(1, len(face) - 1):
                v1, v2, v3 = vertices[face[0]], vertices[face[i]], vertices[face[i + 1]]
                if is_3d:
                    total_area += Triangle3D(v1, v2, v3).area()
                else:
                    # 2D cross product area
                    total_area += abs(0.5 * ((v2.x - v1.x) * (v3.y - v1.y) - (v2.y - v1.y) * (v3.x - v1.x)))

        return total_area

    @staticmethod
    def volume(mesh: Mesh) -> float:
        """Calculates the volume of the mesh.

        For SurfaceMesh, it uses the signed volume of tetrahedra (assumes closed manifold).
        For TetMesh/HexMesh, it sums the volumes of individual cells.
        """
        vertices = mesh.vertices
        if not vertices or not isinstance(vertices[0], Point3D):
            return 0.0

        origin = Point3D(0, 0, 0)
        total_volume = 0.0

        if mesh.cells:
            # TetMesh or HexMesh
            from compgeom.kernel.hexahedron import volume as hex_volume

            for cell in mesh.cells:
                if len(cell) == 4:
                    total_volume += abs(
                        tet_volume(vertices[cell[0]], vertices[cell[1]], vertices[cell[2]], vertices[cell[3]])
                    )
                elif len(cell) == 8:
                    v = [vertices[i] for i in cell]
                    total_volume += abs(hex_volume(v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))
        elif mesh.faces:
            # SurfaceMesh (signed volume)
            for face in mesh.faces:
                if len(face) < 3:
                    continue
                # Triangulate and add signed volume of tetrahedron (origin, v1, v2, v3)
                for i in range(1, len(face) - 1):
                    v1, v2, v3 = vertices[face[0]], vertices[face[i]], vertices[face[i + 1]]
                    total_volume += tet_volume(v1, v2, v3, origin)

        return abs(total_volume)
