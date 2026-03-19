from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Union, Optional

from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.math_utils import EPSILON
from compgeom.kernel.ray import Ray


@dataclass(frozen=True, slots=True)
class AABB2D:
    """Axis-Aligned Bounding Box in 2D."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def center(self) -> Point2D:
        return Point2D((self.min_x + self.max_x) / 2.0, (self.min_y + self.max_y) / 2.0)

    @classmethod
    def from_points(cls, points: List[Point2D]) -> AABB2D:
        if not points:
            raise ValueError("Cannot create AABB from empty list of points.")
        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)
        return cls(min_x, min_y, max_x, max_y)

    def contains_point(self, point: Point2D) -> bool:
        return (self.min_x - EPSILON <= point.x <= self.max_x + EPSILON and
                self.min_y - EPSILON <= point.y <= self.max_y + EPSILON)

    def intersects(self, other: AABB2D) -> bool:
        return not (other.min_x > self.max_x + EPSILON or
                    other.max_x < self.min_x - EPSILON or
                    other.min_y > self.max_y + EPSILON or
                    other.max_y < self.min_y - EPSILON)

    def union(self, other: AABB2D) -> AABB2D:
        return AABB2D(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y)
        )

    def expand_by_point(self, point: Point2D) -> AABB2D:
        return AABB2D(
            min(self.min_x, point.x),
            min(self.min_y, point.y),
            max(self.max_x, point.x),
            max(self.max_y, point.y)
        )

    def intersect_ray(self, ray: Ray[Point2D]) -> Optional[Tuple[float, float]]:
        """
        Return the entry and exit parameters (t_min, t_max) of ray intersection.
        Returns None if there is no intersection.
        """
        t_min = -float('inf')
        t_max = float('inf')

        # Check X and Y slabs
        for origin, direction, b_min, b_max in [
            (ray.origin.x, ray.direction.x, self.min_x, self.max_x),
            (ray.origin.y, ray.direction.y, self.min_y, self.max_y)
        ]:
            if abs(direction) < 1e-12:
                if origin < b_min - EPSILON or origin > b_max + EPSILON:
                    return None
            else:
                t1 = (b_min - origin) / direction
                t2 = (b_max - origin) / direction
                t_min = max(t_min, min(t1, t2))
                t_max = min(t_max, max(t1, t2))

        if t_max < -EPSILON or t_min > t_max + EPSILON:
            return None
            
        return max(0.0, t_min), t_max

    def __repr__(self) -> str:
        return f"AABB2D(min=({self.min_x}, {self.min_y}), max=({self.max_x}, {self.max_y}))"


@dataclass(frozen=True, slots=True)
class AABB3D:
    """Axis-Aligned Bounding Box in 3D."""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def depth(self) -> float:
        return self.max_z - self.min_z

    @property
    def center(self) -> Point3D:
        return Point3D(
            (self.min_x + self.max_x) / 2.0,
            (self.min_y + self.max_y) / 2.0,
            (self.min_z + self.max_z) / 2.0
        )

    @classmethod
    def from_points(cls, points: List[Point3D]) -> AABB3D:
        if not points:
            raise ValueError("Cannot create AABB from empty list of points.")
        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        min_z = min(p.z for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)
        max_z = max(p.z for p in points)
        return cls(min_x, min_y, min_z, max_x, max_y, max_z)

    def contains_point(self, point: Point3D) -> bool:
        return (self.min_x - EPSILON <= point.x <= self.max_x + EPSILON and
                self.min_y - EPSILON <= point.y <= self.max_y + EPSILON and
                self.min_z - EPSILON <= point.z <= self.max_z + EPSILON)

    def intersects(self, other: AABB3D) -> bool:
        return not (other.min_x > self.max_x + EPSILON or
                    other.max_x < self.min_x - EPSILON or
                    other.min_y > self.max_y + EPSILON or
                    other.max_y < self.min_y - EPSILON or
                    other.min_z > self.max_z + EPSILON or
                    other.max_z < self.min_z - EPSILON)

    def union(self, other: AABB3D) -> AABB3D:
        return AABB3D(
            min(self.min_x, other.min_x),
            min(self.min_y, other.min_y),
            min(self.min_z, other.min_z),
            max(self.max_x, other.max_x),
            max(self.max_y, other.max_y),
            max(self.max_z, other.max_z)
        )

    def expand_by_point(self, point: Point3D) -> AABB3D:
        return AABB3D(
            min(self.min_x, point.x),
            min(self.min_y, point.y),
            min(self.min_z, point.z),
            max(self.max_x, point.x),
            max(self.max_y, point.y),
            max(self.max_z, point.z)
        )

    def intersect_ray(self, ray: Ray[Point3D]) -> Optional[Tuple[float, float]]:
        """
        Return the entry and exit parameters (t_min, t_max) of ray intersection.
        Returns None if there is no intersection.
        """
        t_min = -float('inf')
        t_max = float('inf')

        # Check X, Y, and Z slabs
        for origin, direction, b_min, b_max in [
            (ray.origin.x, ray.direction.x, self.min_x, self.max_x),
            (ray.origin.y, ray.direction.y, self.min_y, self.max_y),
            (ray.origin.z, ray.direction.z, self.min_z, self.max_z)
        ]:
            if abs(direction) < 1e-12:
                if origin < b_min - EPSILON or origin > b_max + EPSILON:
                    return None
            else:
                t1 = (b_min - origin) / direction
                t2 = (b_max - origin) / direction
                t_min = max(t_min, min(t1, t2))
                t_max = min(t_max, max(t1, t2))

        if t_max < -EPSILON or t_min > t_max + EPSILON:
            return None
            
        return max(0.0, t_min), t_max

    def __repr__(self) -> str:
        return f"AABB3D(min=({self.min_x}, {self.min_y}, {self.min_z}), max=({self.max_x}, {self.max_y}, {self.max_z}))"


__all__ = ["AABB2D", "AABB3D"]
