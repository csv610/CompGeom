from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Tuple
from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.math_utils import EPSILON
from compgeom.intersect import ray_sphere_intersect

PointType = TypeVar('PointType', 'Point2D', 'Point3D')

@dataclass(frozen=True, slots=True)
class Ray(Generic[PointType]):
    origin: PointType; direction: PointType
    def __post_init__(self):
        d_len = self.direction.length()
        if d_len < EPSILON: raise ValueError("Direction vector cannot be zero.")
        object.__setattr__(self, 'direction', self.direction / d_len)
    def point_at(self, t: float) -> PointType: return self.origin + self.direction * max(0.0, t)
    def intersect_sphere(self, center: PointType, radius: float) -> Optional[Tuple[float, float]]:
        if not isinstance(self.origin, Point3D): return None
        return ray_sphere_intersect((self.origin.x, self.origin.y, self.origin.z),
                                  (self.direction.x, self.direction.y, self.direction.z),
                                  (center.x, center.y, center.z), radius)
    def __repr__(self) -> str: return f"Ray(o={self.origin}, d={self.direction})"

__all__ = ["Ray"]
