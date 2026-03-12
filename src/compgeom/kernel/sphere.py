from __future__ import annotations
import math
from typing import Optional, TYPE_CHECKING, Tuple, List
from decimal import Decimal

if TYPE_CHECKING:
    from .geometry import Point3D

from .math_utils import EPSILON

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
    from .tetrahedron import orientation_sign
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

__all__ = ['insphere_det', 'insphere_sign', 'in_sphere']