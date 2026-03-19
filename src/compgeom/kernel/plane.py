from __future__ import annotations
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from compgeom.kernel.point import Point3D
from compgeom.kernel.math_utils import EPSILON

@dataclass(frozen=True, slots=True)
class Plane:
    """A plane in 3D space defined by the equation ax + by + cz + d = 0."""
    normal: Point3D
    d: float

    @staticmethod
    def from_point_and_normal(point: Point3D, normal: Point3D) -> Plane:
        """Create a plane from a point on the plane and a normal vector."""
        n_len = normal.length()
        if n_len < EPSILON:
            raise ValueError("Normal vector cannot be zero.")
        unit_normal = normal / n_len
        d = -unit_normal.dot(point)
        return Plane(unit_normal, d)

    @staticmethod
    def from_points(p1: Point3D, p2: Point3D, p3: Point3D) -> Plane:
        """Create a plane from three non-collinear points."""
        v1 = p2 - p1
        v2 = p3 - p1
        normal = v1.cross(v2)
        return Plane.from_point_and_normal(p1, normal)

    def signed_distance(self, point: Point3D) -> float:
        """Return the signed distance from the point to the plane."""
        return self.normal.dot(point) + self.d

    def distance(self, point: Point3D) -> float:
        """Return the absolute distance from the point to the plane."""
        return abs(self.signed_distance(point))

    def project_point(self, point: Point3D) -> Point3D:
        """Project a point onto the plane."""
        dist = self.signed_distance(point)
        return point - self.normal * dist

    def is_on_plane(self, point: Point3D) -> bool:
        """Check if a point lies on the plane within EPSILON."""
        return abs(self.signed_distance(point)) < EPSILON

    def side(self, point: Point3D) -> int:
        """
        Return the side of the plane the point is on:
        1 for front (direction of normal), -1 for back, 0 for on the plane.
        """
        dist = self.signed_distance(point)
        if dist > EPSILON:
            return 1
        if dist < -EPSILON:
            return -1
        return 0

    def intersect_ray(self, ray: Ray3D) -> Optional[float]:
        """Return the parameter t of the intersection between the ray and the plane."""
        dot_nd = self.normal.dot(ray.direction)
        if abs(dot_nd) < EPSILON:
            # Ray is parallel to the plane
            return None
        
        t = -(self.normal.dot(ray.origin) + self.d) / dot_nd
        if t < -EPSILON:
            return None
        return max(0.0, t)

    def intersect_plane(self, other: Plane) -> Optional[tuple[Point3D, Point3D]]:
        """
        Return a point on the line of intersection and the direction of the line.
        Returns None if planes are parallel.
        """
        direction = self.normal.cross(other.normal)
        det = direction.length_sq()
        if det < EPSILON:
            return None
        
        # Intersection point: using the formula for intersection of two planes
        # The point is ( (d1*n2 - d2*n1) x (n1 x n2) ) / |n1 x n2|^2
        # where d1, d2 are distances from origin (-Plane.d)
        point = (other.normal * (-self.d) - self.normal * (-other.d)).cross(direction) / det
        return point, direction / math.sqrt(det)

    def __repr__(self) -> str:
        return f"Plane(n={self.normal}, d={self.d})"

__all__ = ["Plane"]
