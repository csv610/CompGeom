from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, TYPE_CHECKING
from compgeom.kernel.point import Point3D
from compgeom.intersect import tri_tetra_intersect

@dataclass(frozen=True, slots=True)
class Tetrahedron:
    v1: Point3D; v2: Point3D; v3: Point3D; v4: Point3D
    @property
    def vertices(self) -> Tuple[Point3D, Point3D, Point3D, Point3D]: return (self.v1, self.v2, self.v3, self.v4)
    def centroid(self) -> Point3D:
        return Point3D(sum(v.x for v in self.vertices)/4, sum(v.y for v in self.vertices)/4, sum(v.z for v in self.vertices)/4)
    def intersect_triangle(self, tri_v: Tuple[Point3D, Point3D, Point3D]) -> bool:
        return tri_tetra_intersect(tri_v, self.vertices)
    def __repr__(self) -> str: return f"Tetrahedron({self.v1}, {self.v2}, {self.v3}, {self.v4})"

__all__ = ["Tetrahedron"]
