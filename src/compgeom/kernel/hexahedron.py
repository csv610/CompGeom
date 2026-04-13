from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Any
from compgeom.kernel.point import Point3D
from compgeom.intersect import tri_hex_intersect

@dataclass(frozen=True, slots=True)
class Hexahedron:
    v1: Point3D; v2: Point3D; v3: Point3D; v4: Point3D
    v5: Point3D; v6: Point3D; v7: Point3D; v8: Point3D
    @property
    def vertices(self) -> Tuple[Point3D, ...]:
        return (self.v1, self.v2, self.v3, self.v4, self.v5, self.v6, self.v7, self.v8)
    def intersect_triangle(self, tri_v: Tuple[Point3D, Point3D, Point3D]) -> bool:
        return tri_hex_intersect(tri_v, self.vertices)
    def __repr__(self) -> str: return f"Hexahedron({self.v1}, ..., {self.v8})"

__all__ = ["Hexahedron"]
