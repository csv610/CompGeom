from __future__ import annotations
import math
from typing import Tuple, Optional, List, TYPE_CHECKING

from compgeom.kernel import Point2D, Point3D

def intersect_segments_2d(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Optional[Point2D]:
    """Intersection of two 2D line segments. Returns intersection point or None."""
    den = (p1.x-p2.x)*(p3.y-p4.y)-(p1.y-p2.y)*(p3.x-p4.x)
    if abs(den) < 1e-12: return None
    t = ((p1.x-p3.x)*(p3.y-p4.y)-(p1.y-p3.y)*(p3.x-p4.x))/den
    u = -((p1.x-p2.x)*(p1.y-p3.y)-(p1.y-p2.y)*(p1.x-p3.x))/den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return Point2D(p1.x + t*(p2.x-p1.x), p1.y + t*(p2.y-p1.y))
    return None

def intersect_proper_2d(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> bool:
    """Check if segments AB and CD intersect properly (not at endpoints)."""
    from compgeom.kernel import cross_product
    o1, o2 = cross_product(p1, p2, p3), cross_product(p1, p2, p4)
    o3, o4 = cross_product(p3, p4, p1), cross_product(p3, p4, p2)
    return (o1 > 1e-9) != (o2 > 1e-9) and (o3 > 1e-9) != (o4 > 1e-9)

def ray_segment_intersect_2d(origin: Point2D, direction: Point2D, start: Point2D, end: Point2D) -> Optional[float]:
    """Intersection of a 2D ray and a 2D segment. Returns t."""
    edge = Point2D(end.x - start.x, end.y - start.y)
    den = direction.x * edge.y - direction.y * edge.x
    if abs(den) < 1e-12: return None
    t = ((start.x - origin.x) * edge.y - (start.y - origin.y) * edge.x) / den
    u = ((start.x - origin.x) * direction.y - (start.y - origin.y) * direction.x) / den
    return t if t >= 0 and 0 <= u <= 1 else None

def segment_plane_intersect_3d(start: Point3D, end: Point3D, plane_p: Point3D, plane_n: Point3D) -> Optional[Point3D]:
    """Intersection of a 3D segment and a plane."""
    v = end - start
    denom = v.x*plane_n.x + v.y*plane_n.y + v.z*plane_n.z
    if abs(denom) < 1e-12: return None
    t = ((plane_p.x-start.x)*plane_n.x + (plane_p.y-start.y)*plane_n.y + (plane_p.z-start.z)*plane_n.z) / denom
    if 0 <= t <= 1:
        return start + v * t
    return None
