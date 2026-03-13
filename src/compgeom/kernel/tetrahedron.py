from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING, Tuple, List, Any
from decimal import Decimal

if TYPE_CHECKING:
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

__all__ = ["orientation", "orientation_sign", "volume", "contains_point"]