from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Optional, Tuple, Generic, TypeVar
from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.math_utils import EPSILON
from compgeom.intersect import intersect_segments_2d, intersect_proper_2d, ray_segment_intersect_2d

PointType = TypeVar('PointType', 'Point2D', 'Point3D')

@dataclass(frozen=True, slots=True)
class LineSegment(Generic[PointType]):
    start: PointType; end: PointType
    def length(self) -> float: return self.start.distance_to(self.end)
    def midpoint(self) -> PointType: return (self.start + self.end) * 0.5
    def __repr__(self) -> str: return f"LineSegment({self.start} -> {self.end})"

def intersect_lines(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Optional[Point2D]:
    return intersect_segments_2d(p1, p2, p3, p4)

def intersect_proper(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    return intersect_proper_2d(a, b, c, d)

def intersect_ray(origin: Point2D, angle: float, start: Point2D, end: Point2D) -> Tuple[float, Point2D] | None:
    dir = Point2D(math.cos(angle), math.sin(angle))
    t = ray_segment_intersect_2d(origin, dir, start, end)
    return (t, origin + dir * t) if t is not None else None

__all__ = ["LineSegment", "intersect_lines", "intersect_proper", "intersect_ray"]
