from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple, List, Optional

from compgeom.kernel.point import Point2D, Point3D


@dataclass(frozen=True, slots=True)
class Transformation:
    """A 4x4 transformation matrix for 3D and 2D operations."""
    # Row-major order
    m00: float = 1.0; m01: float = 0.0; m02: float = 0.0; m03: float = 0.0
    m10: float = 0.0; m11: float = 1.0; m12: float = 0.0; m13: float = 0.0
    m20: float = 0.0; m21: float = 0.0; m22: float = 1.0; m23: float = 0.0
    m30: float = 0.0; m31: float = 0.0; m32: float = 0.0; m33: float = 1.0

    @classmethod
    def translation(cls, dx: float, dy: float, dz: float = 0.0) -> Transformation:
        return cls(m03=dx, m13=dy, m23=dz)

    @classmethod
    def scale(cls, sx: float, sy: float, sz: float = 1.0) -> Transformation:
        return cls(m00=sx, m11=sy, m22=sz)

    @classmethod
    def rotation_z(cls, angle: float) -> Transformation:
        """Create a rotation matrix around the Z-axis."""
        c = math.cos(angle)
        s = math.sin(angle)
        return cls(m00=c, m01=-s, m10=s, m11=c)

    @classmethod
    def rotation_x(cls, angle: float) -> Transformation:
        """Create a rotation matrix around the X-axis."""
        c = math.cos(angle)
        s = math.sin(angle)
        return cls(m11=c, m12=-s, m21=s, m22=c)

    @classmethod
    def rotation_y(cls, angle: float) -> Transformation:
        """Create a rotation matrix around the Y-axis."""
        c = math.cos(angle)
        s = math.sin(angle)
        return cls(m00=c, m02=s, m20=-s, m22=c)

    def multiply(self, other: Transformation) -> Transformation:
        """Return the product of this matrix and another."""
        res = [0.0] * 16
        a = self.to_list()
        b = [
            other.m00, other.m01, other.m02, other.m03,
            other.m10, other.m11, other.m12, other.m13,
            other.m20, other.m21, other.m22, other.m23,
            other.m30, other.m31, other.m32, other.m33
        ]
        
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    res[i*4 + j] += a[i*4 + k] * b[k*4 + j]
        
        return Transformation(*res)

    def to_list(self) -> List[float]:
        """Return matrix elements as a flat list in row-major order."""
        return [
            self.m00, self.m01, self.m02, self.m03,
            self.m10, self.m11, self.m12, self.m13,
            self.m20, self.m21, self.m22, self.m23,
            self.m30, self.m31, self.m32, self.m33
        ]

    def determinant(self) -> float:
        """Calculate the determinant of the 4x4 matrix."""
        m = self.to_list()
        
        def det3(a, b, c, d, e, f, g, h, i):
            return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)

        return (m[0] * det3(m[5], m[6], m[7], m[9], m[10], m[11], m[13], m[14], m[15]) -
                m[1] * det3(m[4], m[6], m[7], m[8], m[10], m[11], m[12], m[14], m[15]) +
                m[2] * det3(m[4], m[5], m[7], m[8], m[9], m[11], m[12], m[13], m[15]) -
                m[3] * det3(m[4], m[5], m[6], m[8], m[9], m[10], m[12], m[13], m[14]))

    def inverse(self) -> Optional[Transformation]:
        """Return the inverse of the transformation matrix, or None if singular."""
        det = self.determinant()
        if abs(det) < 1e-15:
            return None

        m = self.to_list()
        res = [0.0] * 16

        # Sub-determinants for the adjugate matrix
        def det3(a, b, c, d, e, f, g, h, i):
            return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)

        # Adjugate matrix (transpose of cofactor matrix)
        res[0] = det3(m[5], m[6], m[7], m[9], m[10], m[11], m[13], m[14], m[15])
        res[1] = -det3(m[1], m[2], m[3], m[9], m[10], m[11], m[13], m[14], m[15])
        res[2] = det3(m[1], m[2], m[3], m[5], m[6], m[7], m[13], m[14], m[15])
        res[3] = -det3(m[1], m[2], m[3], m[5], m[6], m[7], m[9], m[10], m[11])

        res[4] = -det3(m[4], m[6], m[7], m[8], m[10], m[11], m[12], m[14], m[15])
        res[5] = det3(m[0], m[2], m[3], m[8], m[10], m[11], m[12], m[14], m[15])
        res[6] = -det3(m[0], m[2], m[3], m[4], m[6], m[7], m[12], m[14], m[15])
        res[7] = det3(m[0], m[2], m[3], m[4], m[6], m[7], m[8], m[10], m[11])

        res[8] = det3(m[4], m[5], m[7], m[8], m[9], m[11], m[12], m[13], m[15])
        res[9] = -det3(m[0], m[1], m[3], m[8], m[9], m[11], m[12], m[13], m[15])
        res[10] = det3(m[0], m[1], m[3], m[4], m[5], m[7], m[12], m[13], m[15])
        res[11] = -det3(m[0], m[1], m[3], m[4], m[5], m[7], m[8], m[9], m[11])

        res[12] = -det3(m[4], m[5], m[6], m[8], m[9], m[10], m[12], m[13], m[14])
        res[13] = det3(m[0], m[1], m[2], m[8], m[9], m[10], m[12], m[13], m[14])
        res[14] = -det3(m[0], m[1], m[2], m[4], m[5], m[6], m[12], m[13], m[14])
        res[15] = det3(m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10])

        inv_det = 1.0 / det
        return Transformation(*(r * inv_det for r in res))

    def apply_to_point3d(self, p: Point3D) -> Point3D:
        """Transform a 3D point."""
        x = self.m00 * p.x + self.m01 * p.y + self.m02 * p.z + self.m03
        y = self.m10 * p.x + self.m11 * p.y + self.m12 * p.z + self.m13
        z = self.m20 * p.x + self.m21 * p.y + self.m22 * p.z + self.m23
        w = self.m30 * p.x + self.m31 * p.y + self.m32 * p.z + self.m33
        if abs(w - 1.0) > 1e-12 and abs(w) > 1e-12:
            return Point3D(x / w, y / w, z / w, p.id)
        return Point3D(x, y, z, p.id)

    def apply_to_point2d(self, p: Point2D) -> Point2D:
        """Transform a 2D point (treating it as Z=0)."""
        x = self.m00 * p.x + self.m01 * p.y + self.m03
        y = self.m10 * p.x + self.m11 * p.y + self.m13
        w = self.m30 * p.x + self.m31 * p.y + self.m33
        if abs(w - 1.0) > 1e-12 and abs(w) > 1e-12:
            return Point2D(x / w, y / w, p.id)
        return Point2D(x, y, p.id)


__all__ = ["Transformation"]
