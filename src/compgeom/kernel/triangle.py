from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Tuple, List, Any
from decimal import Decimal

from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.math_utils import EPSILON, cross_product, distance
from compgeom.intersect import ray_triangle_intersect

if TYPE_CHECKING:
    from compgeom.kernel.ray import Ray

@dataclass(frozen=True, slots=True)
class Triangle2D:
    v1: Point2D; v2: Point2D; v3: Point2D
    @property
    def vertices(self) -> Tuple[Point2D, Point2D, Point2D]: return (self.v1, self.v2, self.v3)
    def area(self) -> float: return area(self.v1, self.v2, self.v3)
    def contains_point(self, p: Point2D) -> bool: return contains_point(self.v1, self.v2, self.v3, p)
    def __repr__(self) -> str: return f"Triangle2D({self.v1}, {self.v2}, {self.v3})"

@dataclass(frozen=True, slots=True)
class Triangle3D:
    v1: Point3D; v2: Point3D; v3: Point3D
    @property
    def vertices(self) -> Tuple[Point3D, Point3D, Point3D]: return (self.v1, self.v2, self.v3)
    def area(self) -> float:
        e1, e2 = self.v2 - self.v1, self.v3 - self.v1
        return 0.5 * e1.cross(e2).length()
    def intersect_ray(self, ray: Ray[Point3D]) -> Optional[float]:
        res = ray_triangle_intersect((ray.origin.x, ray.origin.y, ray.origin.z), 
                                   (ray.direction.x, ray.direction.y, ray.direction.z),
                                   (self.v1.x, self.v1.y, self.v1.z),
                                   (self.v2.x, self.v2.y, self.v2.z),
                                   (self.v3.x, self.v3.y, self.v3.z))
        return res[0] if res else None
    def __repr__(self) -> str: return f"Triangle3D({self.v1}, {self.v2}, {self.v3})"

def orientation(a: Point2D, b: Point2D, c: Point2D) -> float:
    return 0.5 * cross_product(a, b, c)

def area(a: Point2D, b: Point2D, c: Point2D) -> float:
    return abs(orientation(a, b, c))

def contains_point(v1: Point2D, v2: Point2D, v3: Point2D, p: Point2D) -> bool:
    def sign(p1, p2, p3): return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
    d1 = sign(p, v1, v2); d2 = sign(p, v2, v3); d3 = sign(p, v3, v1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

__all__ = ["Triangle2D", "Triangle3D", "area", "contains_point"]
