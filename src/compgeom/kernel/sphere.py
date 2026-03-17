from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Optional, TYPE_CHECKING, Tuple, List
from decimal import Decimal

from .point import Point3D
from .math_utils import EPSILON, distance_3d
from .tetrahedron import orientation_sign


@dataclass(frozen=True, slots=True)
class Sphere:
    center: Point3D
    radius: float

    def contains_point(self, point: Point3D) -> bool:
        return distance_3d(self.center, point) <= self.radius + EPSILON

    def __repr__(self) -> str:
        return f"Sphere(c={self.center}, r={self.radius})"


def from_two_points(p1: Point3D, p2: Point3D) -> Sphere:
    """Return the smallest sphere defined by two points as diameter."""
    center = Point3D(
        (p1.x + p2.x) / 2.0,
        (p1.y + p2.y) / 2.0,
        (p1.z + p2.z) / 2.0
    )
    return Sphere(center, distance_3d(p1, p2) / 2.0)


def from_three_points(p1: Point3D, p2: Point3D, p3: Point3D) -> Sphere:
    """Return the smallest sphere with three points on its surface (circumcircle in 3D)."""
    # Finding the circumcenter of the triangle in 3D
    # The center lies on the plane of the triangle
    v1 = p2 - p1
    v2 = p3 - p1
    v1v1 = v1.dot(v1)
    v2v2 = v2.dot(v2)
    v1v2 = v1.dot(v2)
    
    denominator = 2.0 * (v1v1 * v2v2 - v1v2 * v1v2)
    if abs(denominator) < 1e-12:
        # Collinear points: fallback to two furthest points
        d12 = distance_3d(p1, p2)
        d13 = distance_3d(p1, p3)
        d23 = distance_3d(p2, p3)
        if d12 >= d13 and d12 >= d23: return from_two_points(p1, p2)
        if d13 >= d12 and d13 >= d23: return from_two_points(p1, p3)
        return from_two_points(p2, p3)
        
    alpha = (v1v1 * v2v2 - v2v2 * v1v2) / denominator
    beta = (v2v2 * v1v1 - v1v1 * v1v2) / denominator
    
    # Correct formula for circumcenter in plane
    a = v1v1 * v2v2 - v1v2 * v1v2
    k1 = v1v1 * (v2v2 - v1v2) / (2.0 * a)
    k2 = v2v2 * (v1v1 - v1v2) / (2.0 * a)
    center = p1 + v1 * k1 + v2 * k2
    return Sphere(center, distance_3d(center, p1))


def from_four_points(p1: Point3D, p2: Point3D, p3: Point3D, p4: Point3D) -> Sphere:
    """Return the circumsphere of a tetrahedron."""
    # Using the property that the circumcenter is equidistant from all vertices.
    # We solve a system of linear equations.
    # (x - x1)^2 + (y - y1)^2 + (z - z1)^2 = R^2
    # Subtracting equations gives linear system:
    # 2x(x2-x1) + 2y(y2-y1) + 2z(z2-z1) = x2^2+y2^2+z2^2 - (x1^2+y1^2+z1^2)
    
    def get_row(pa, pb):
        return [
            2 * (pb.x - pa.x),
            2 * (pb.y - pa.y),
            2 * (pb.z - pa.z),
            pb.x**2 + pb.y**2 + pb.z**2 - (pa.x**2 + pa.y**2 + pa.z**2)
        ]
        
    m = [get_row(p1, p2), get_row(p1, p3), get_row(p1, p4)]
    
    # Solve 3x3 system using Cramer's rule or similar
    def det3(a, b, c):
        return (a[0] * (b[1] * c[2] - b[2] * c[1]) -
                a[1] * (b[0] * c[2] - b[2] * c[0]) +
                a[2] * (b[0] * c[1] - b[1] * c[0]))
                
    d = det3(m[0], m[1], m[2])
    if abs(d) < 1e-12:
        # Coplanar points: fallback to smallest sphere of 3 points
        pts = [p1, p2, p3, p4]
        candidates = []
        for i in range(4):
            for j in range(i+1, 4):
                for k in range(j+1, 4):
                    candidates.append(from_three_points(pts[i], pts[j], pts[k]))
        return min(candidates, key=lambda s: s.radius)

    dx = det3([m[0][3], m[0][1], m[0][2]], [m[1][3], m[1][1], m[1][2]], [m[2][3], m[2][1], m[2][2]])
    dy = det3([m[0][0], m[0][3], m[0][2]], [m[1][0], m[1][3], m[1][2]], [m[2][0], m[2][3], m[2][2]])
    dz = det3([m[0][0], m[0][1], m[0][3]], [m[1][0], m[1][1], m[1][3]], [m[2][0], m[2][1], m[2][3]])
    
    center = Point3D(dx / d, dy / d, dz / d)
    return Sphere(center, distance_3d(center, p1))

def _decimal_insphere(a: Point3D, b: Point3D, c: Point3D, d: Point3D, e: Point3D) -> Decimal:
    ax, ay, az = Decimal(str(a.x)) - Decimal(str(e.x)), Decimal(str(a.y)) - Decimal(str(e.y)), Decimal(str(a.z)) - Decimal(str(e.z))
    bx, by, bz = Decimal(str(b.x)) - Decimal(str(e.x)), Decimal(str(b.y)) - Decimal(str(e.y)), Decimal(str(b.z)) - Decimal(str(e.z))
    cx, cy, cz = Decimal(str(c.x)) - Decimal(str(e.x)), Decimal(str(c.y)) - Decimal(str(e.y)), Decimal(str(c.z)) - Decimal(str(e.z))
    dx, dy, dz = Decimal(str(d.x)) - Decimal(str(e.x)), Decimal(str(d.y)) - Decimal(str(e.y)), Decimal(str(d.z)) - Decimal(str(e.z))
    
    a2 = ax*ax + ay*ay + az*az
    b2 = bx*bx + by*by + bz*bz
    c2 = cx*cx + cy*cy + cz*cz
    d2 = dx*dx + dy*dy + dz*dz
    
    def det3(m00, m01, m02, m10, m11, m12, m20, m21, m22):
        return (m00 * (m11 * m22 - m12 * m21) -
                m01 * (m10 * m22 - m12 * m20) +
                m02 * (m10 * m21 - m11 * m20))

    return (-a2 * det3(bx, by, bz, cx, cy, cz, dx, dy, dz) +
             b2 * det3(ax, ay, az, cx, cy, cz, dx, dy, dz) -
             c2 * det3(ax, ay, az, bx, by, bz, dx, dy, dz) +
             d2 * det3(ax, ay, az, bx, by, bz, cx, cy, cz))

def insphere_det(a: Point3D, b: Point3D, c: Point3D, d: Point3D, e: Point3D) -> float:
    ax, ay, az = a.x - e.x, a.y - e.y, a.z - e.z
    bx, by, bz = b.x - e.x, b.y - e.y, b.z - e.z
    cx, cy, cz = c.x - e.x, c.y - e.y, c.z - e.z
    dx, dy, dz = d.x - e.x, d.y - e.y, d.z - e.z
    
    a2 = ax*ax + ay*ay + az*az
    b2 = bx*bx + by*by + bz*bz
    c2 = cx*cx + cy*cy + cz*cz
    d2 = dx*dx + dy*dy + dz*dz
    
    def det3(m00, m01, m02, m10, m11, m12, m20, m21, m22):
        return (m00 * (m11 * m22 - m12 * m21) -
                m01 * (m10 * m22 - m12 * m20) +
                m02 * (m10 * m21 - m11 * m20))

    det = (-a2 * det3(bx, by, bz, cx, cy, cz, dx, dy, dz) +
            b2 * det3(ax, ay, az, cx, cy, cz, dx, dy, dz) -
            c2 * det3(ax, ay, az, bx, by, bz, dx, dy, dz) +
            d2 * det3(ax, ay, az, bx, by, bz, cx, cy, cz))
           
    if abs(det) > EPSILON:
        return det
    return float(_decimal_insphere(a, b, c, d, e))

def insphere_sign(a: Point3D, b: Point3D, c: Point3D, d: Point3D, e: Point3D) -> int:
    det = insphere_det(a, b, c, d, e)
    orient = orientation_sign(a, b, c, d)
    adjusted = det * orient
    if adjusted > EPSILON: return 1
    if adjusted < -EPSILON: return -1
    exact = _decimal_insphere(a, b, c, d, e)
    if orient < 0: exact = -exact
    if exact > 0: return 1
    if exact < 0: return -1
    return 0

def in_sphere(a: Point3D, b: Point3D, c: Point3D, d: Point3D, e: Point3D) -> bool:
    return insphere_sign(a, b, c, d, e) > 0

__all__ = ['Sphere', 'from_two_points', 'from_three_points', 'from_four_points', 'insphere_det', 'insphere_sign', 'in_sphere']
