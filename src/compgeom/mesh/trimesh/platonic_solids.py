"""Generation of Platonic Solids meshes."""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, List, Tuple

from ...kernel import Point3D

if TYPE_CHECKING:
    from ..mesh import TriangleMesh


class PlatonicSolid:
    """Generates meshes for the five Platonic solids."""

    @staticmethod
    def _create_mesh(vertices: List[Point3D], faces: List[Tuple[int, int, int]]) -> TriangleMesh:
        from ..mesh import TriangleMesh
        return TriangleMesh(vertices, faces)

    @staticmethod
    def tetrahedron(size: float = 1.0) -> TriangleMesh:
        """Generates a regular tetrahedron mesh."""
        s = size / math.sqrt(3)
        v = [
            Point3D(s, s, s, id=0),
            Point3D(s, -s, -s, id=1),
            Point3D(-s, s, -s, id=2),
            Point3D(-s, -s, s, id=3)
        ]
        f = [(0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)]
        return PlatonicSolid._create_mesh(v, f)

    @staticmethod
    def cube(size: float = 1.0) -> TriangleMesh:
        """Generates a cube (hexahedron) mesh."""
        s = size / 2.0
        v = [
            Point3D(-s, -s, -s, id=0), Point3D(s, -s, -s, id=1),
            Point3D(s, s, -s, id=2), Point3D(-s, s, -s, id=3),
            Point3D(-s, -s, s, id=4), Point3D(s, -s, s, id=5),
            Point3D(s, s, s, id=6), Point3D(-s, s, s, id=7)
        ]
        f = [
            (0, 3, 2), (0, 2, 1), (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4), (2, 3, 7), (2, 7, 6),
            (0, 4, 7), (0, 7, 3), (1, 2, 6), (1, 6, 5)
        ]
        return PlatonicSolid._create_mesh(v, f)

    @staticmethod
    def octahedron(size: float = 1.0) -> TriangleMesh:
        """Generates a regular octahedron mesh."""
        s = size / math.sqrt(2)
        v = [
            Point3D(s, 0, 0, id=0), Point3D(-s, 0, 0, id=1),
            Point3D(0, s, 0, id=2), Point3D(0, -s, 0, id=3),
            Point3D(0, 0, s, id=4), Point3D(0, 0, -s, id=5)
        ]
        f = [
            (4, 0, 2), (4, 2, 1), (4, 1, 3), (4, 3, 0),
            (5, 2, 0), (5, 1, 2), (5, 3, 1), (5, 0, 3)
        ]
        return PlatonicSolid._create_mesh(v, f)

    @staticmethod
    def icosahedron(size: float = 1.0) -> TriangleMesh:
        """Generates a regular icosahedron mesh."""
        phi = (1 + math.sqrt(5)) / 2.0
        scale = size / math.sqrt(1 + phi**2)
        v = [
            Point3D(0, -scale, phi*scale, id=0), Point3D(0, scale, phi*scale, id=1),
            Point3D(0, -scale, -phi*scale, id=2), Point3D(0, scale, -phi*scale, id=3),
            Point3D(-scale, phi*scale, 0, id=4), Point3D(scale, phi*scale, 0, id=5),
            Point3D(-scale, -phi*scale, 0, id=6), Point3D(scale, -phi*scale, 0, id=7),
            Point3D(phi*scale, 0, -scale, id=8), Point3D(phi*scale, 0, scale, id=9),
            Point3D(-phi*scale, 0, -scale, id=10), Point3D(-phi*scale, 0, scale, id=11)
        ]
        f = [
            (0, 11, 1), (0, 1, 9), (0, 9, 7), (0, 7, 6), (0, 6, 11),
            (1, 11, 4), (1, 4, 5), (1, 5, 9), (2, 3, 10), (2, 10, 6),
            (2, 6, 7), (2, 7, 8), (2, 8, 3), (3, 8, 5), (3, 5, 4),
            (3, 4, 10), (4, 11, 10), (5, 8, 9), (6, 10, 11), (7, 9, 8)
        ]
        return PlatonicSolid._create_mesh(v, f)

    @staticmethod
    def dodecahedron(size: float = 1.0) -> TriangleMesh:
        """Generates a regular dodecahedron mesh."""
        phi = (1 + math.sqrt(5)) / 2.0
        # Circumradius of a dodecahedron with edge length 2/phi is sqrt(3)
        # So we scale by size/sqrt(3)
        scale = size / math.sqrt(3)
        v = [
            Point3D(scale, scale, scale, id=0), Point3D(scale, scale, -scale, id=1),
            Point3D(scale, -scale, scale, id=2), Point3D(scale, -scale, -scale, id=3),
            Point3D(-scale, scale, scale, id=4), Point3D(-scale, scale, -scale, id=5),
            Point3D(-scale, -scale, scale, id=6), Point3D(-scale, -scale, -scale, id=7),
            Point3D(0, scale / phi, phi * scale, id=8), Point3D(0, scale / phi, -phi * scale, id=9),
            Point3D(0, -scale / phi, phi * scale, id=10), Point3D(0, -scale / phi, -phi * scale, id=11),
            Point3D(scale / phi, phi * scale, 0, id=12), Point3D(scale / phi, -phi * scale, 0, id=13),
            Point3D(-scale / phi, phi * scale, 0, id=14), Point3D(-scale / phi, -phi * scale, 0, id=15),
            Point3D(phi * scale, 0, scale / phi, id=16), Point3D(phi * scale, 0, -scale / phi, id=17),
            Point3D(-phi * scale, 0, scale / phi, id=18), Point3D(-phi * scale, 0, -scale / phi, id=19)
        ]
        pentagons = [
            (8, 0, 12, 14, 4), (10, 2, 13, 15, 6), (11, 3, 13, 15, 7), (9, 1, 12, 14, 5),
            (16, 0, 8, 10, 2), (17, 1, 9, 11, 3), (18, 4, 8, 10, 6), (19, 5, 9, 11, 7),
            (12, 0, 16, 17, 1), (13, 2, 16, 17, 3), (14, 4, 18, 19, 5), (15, 6, 18, 19, 7)
        ]
        f = []
        for p in pentagons:
            f.append((p[0], p[1], p[2]))
            f.append((p[0], p[2], p[3]))
            f.append((p[0], p[3], p[4]))
        return PlatonicSolid._create_mesh(v, f)
