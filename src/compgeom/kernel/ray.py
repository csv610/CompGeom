from __future__ import annotations
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar, Optional

from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.math_utils import EPSILON

PointType = TypeVar('PointType', 'Point2D', 'Point3D')

@dataclass(frozen=True, slots=True)
class Ray(Generic[PointType]):
    """A ray defined by an origin point and a direction vector.
    Can be embedded in 2D or 3D space depending on the PointType.
    """
    origin: PointType
    direction: PointType

    def __post_init__(self):
        # Normalize direction
        d_len = self.direction.length()
        if d_len < EPSILON:
            raise ValueError("Direction vector cannot be zero.")
        # Since frozen=True, we have to use object.__setattr__
        object.__setattr__(self, 'direction', self.direction / d_len)

    def point_at(self, t: float) -> PointType:
        """Return the point at parameter t along the ray."""
        if t < 0:
            return self.origin
        return self.origin + self.direction * t

    def closest_parameter(self, point: PointType) -> float:
        """Return the parameter t of the closest point on the ray to the given point."""
        v = point - self.origin
        return max(0.0, v.dot(self.direction))

    def closest_point(self, point: PointType) -> PointType:
        """Return the closest point on the ray to the given point."""
        return self.point_at(self.closest_parameter(point))

    def distance_to(self, point: PointType) -> float:
        """Return the distance from the point to the ray."""
        return point.distance_to(self.closest_point(point))

    def contains_point(self, point: PointType) -> bool:
        """Check if the point lies on the ray within EPSILON."""
        if self.origin.distance_to(point) < EPSILON:
            return True
        v = point - self.origin
        v_len = v.length()
        dot = v.dot(self.direction)
        return abs(dot - v_len) < EPSILON

    def intersect_sphere(self, center: PointType, radius: float) -> Optional[tuple[float, float]]:
        """
        Return the parameters (t1, t2) of the intersection between the ray and the sphere.
        Returns None if there is no intersection.
        Note: The points must be 3D points for this operation to make geometric sense as a sphere.
        """
        oc = self.origin - center
        a = self.direction.dot(self.direction)
        b = 2.0 * oc.dot(self.direction)
        c = oc.dot(oc) - radius * radius
        
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        
        t1 = (-b - math.sqrt(discriminant)) / (2.0 * a)
        t2 = (-b + math.sqrt(discriminant)) / (2.0 * a)
        
        # Ray logic: only keep intersections where t >= 0
        if t2 < -EPSILON:
            return None
        return max(0.0, t1), t2

    def __repr__(self) -> str:
        return f"Ray(o={self.origin}, d={self.direction})"

__all__ = ["Ray"]
