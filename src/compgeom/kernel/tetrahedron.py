from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING, Tuple, List, Any
from decimal import Decimal

from .point import Point3D

from .math_utils import (
    EPSILON,
)

def _decimal_orientation(a: Point3D, b: Point3D, c: Point3D, d: Point3D) -> Decimal:
    ax, ay, az = Decimal(str(a.x)), Decimal(str(a.y)), Decimal(str(a.z))
    bx, by, bz = Decimal(str(b.x)), Decimal(str(b.y)), Decimal(str(b.z))
    cx, cy, cz = Decimal(str(c.x)), Decimal(str(c.y)), Decimal(str(c.z))
    dx, dy, dz = Decimal(str(d.x)), Decimal(str(d.y)), Decimal(str(d.z))
    
    m00, m01, m02 = ax-dx, ay-dy, az-dz
    m10, m11, m12 = bx-dx, by-dy, bz-dz
    m20, m21, m22 = cx-dx, cy-dy, cz-dz
    
    return (m00 * (m11 * m22 - m12 * m21) -
            m01 * (m10 * m22 - m12 * m20) +
            m02 * (m10 * m21 - m11 * m20))

def orientation(a: Point3D, b: Point3D, c: Point3D, d: Point3D) -> float:
    adx, ady, adz = a.x - d.x, a.y - d.y, a.z - d.z
    bdx, bdy, bdz = b.x - d.x, b.y - d.y, b.z - d.z
    cdx, cdy, cdz = c.x - d.x, c.y - d.y, c.z - d.z
    
    det = (adx * (bdy * cdz - bdz * cdy) -
           ady * (bdx * cdz - bdz * cdx) +
           adz * (bdx * cdy - bdy * cdx))
           
    if abs(det) > EPSILON:
        return det
    return float(_decimal_orientation(a, b, c, d))

def orientation_sign(a: Point3D, b: Point3D, c: Point3D, d: Point3D) -> int:
    val = orientation(a, b, c, d)
    if val > EPSILON: return 1
    if val < -EPSILON: return -1
    exact = _decimal_orientation(a, b, c, d)
    if exact > 0: return 1
    if exact < 0: return -1
    return 0

def volume(a: Point3D, b: Point3D, c: Point3D, d: Point3D) -> float:
    return orientation(a, b, c, d) / 6.0

def contains_point(a, b=None, c=None, d=None, p=None) -> bool:
    if c is None:
        v0, v1, v2, v3 = a.vertices
        pt = b
    else:
        v0, v1, v2, v3, pt = a, b, c, d, p
    
    s0 = orientation_sign(v1, v2, v3, pt)
    s1 = orientation_sign(v0, v3, v2, pt)
    s2 = orientation_sign(v0, v1, v3, pt)
    s3 = orientation_sign(v0, v2, v1, pt)
    ref_sign = orientation_sign(v0, v1, v2, v3)
    if ref_sign == 0: return False
    return (s0*ref_sign >= -EPSILON and s1*ref_sign >= -EPSILON and s2*ref_sign >= -EPSILON and s3*ref_sign >= -EPSILON)

def barycentric_coords(p: Point3D, a: Point3D, b: Point3D, c: Point3D, d: Point3D) -> Tuple[float, float, float]:
    """
    Return the barycentric coordinates (u, v, w) of point p with respect to tetrahedron (a, b, c, d).
    P = a + u(b-a) + v(c-a) + w(d-a)
    The 4th coordinate is 1 - u - v - w.
    """
    v0 = b - a
    v1 = c - a
    v2 = d - a
    vp = p - a
    
    # Solve system of 3 linear equations (3D vectors)
    # Using Cramer's rule on the 3x3 determinant
    def det3(c1, c2, c3):
        return (c1.x * (c2.y * c3.z - c2.z * c3.y) -
                c1.y * (c2.x * c3.z - c2.z * c3.x) +
                c1.z * (c2.x * c3.y - c2.y * c3.x))
    
    det_main = det3(v0, v1, v2)
    if abs(det_main) < 1e-12:
        return (0.0, 0.0, 0.0) # Degenerate tetrahedron
        
    u = det3(vp, v1, v2) / det_main
    v = det3(v0, vp, v2) / det_main
    w = det3(v0, v1, vp) / det_main
    
    return u, v, w

__all__ = ["orientation", "orientation_sign", "volume", "contains_point", "barycentric_coords"]
