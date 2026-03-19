from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple, List

from compgeom.kernel.point import Point3D
from compgeom.kernel.math_utils import EPSILON
from compgeom.kernel.tetrahedron import volume as tet_volume, orientation_sign
from compgeom.kernel.sphere import Sphere, from_two_points, from_three_points, from_four_points


@dataclass(frozen=True, slots=True)
class Hexahedron:
    """
    A hexahedron defined by 8 vertices.
    Vertices v1-v4 form the bottom face, and v5-v8 form the top face,
    both in counter-clockwise order when viewed from outside.
    """
    v1: Point3D
    v2: Point3D
    v3: Point3D
    v4: Point3D
    v5: Point3D
    v6: Point3D
    v7: Point3D
    v8: Point3D

    @property
    def vertices(self) -> Tuple[Point3D, ...]:
        return (self.v1, self.v2, self.v3, self.v4, self.v5, self.v6, self.v7, self.v8)

    def centroid(self) -> Point3D:
        """Return the centroid of the hexahedron."""
        return centroid(*self.vertices)

    def volume(self) -> float:
        """Return the volume of the hexahedron."""
        return volume(*self.vertices)

    def is_convex(self) -> bool:
        """Check if the hexahedron is convex."""
        return is_convex(*self.vertices)

    def contains_point(self, p: Point3D) -> bool:
        """Check if point p is inside the hexahedron."""
        return contains_point(p, *self.vertices)

    def faces(self) -> Tuple[Tuple[Point3D, Point3D, Point3D, Point3D], ...]:
        """Return the 6 faces of the hexahedron as tuples of 4 points."""
        return faces(*self.vertices)

    def edges(self) -> Tuple[Tuple[Point3D, Point3D], ...]:
        """Return the 12 edges of the hexahedron as tuples of 2 points."""
        return edges(*self.vertices)

    def min_sphere(self) -> Sphere:
        """Return the minimum bounding sphere of the hexahedron."""
        return min_sphere(*self.vertices)

    def barycentric_coords(self, p: Point3D) -> Tuple[float, float, float]:
        """Return the trilinear coordinates (u, v, w) of point p."""
        return barycentric_coords(p, *self.vertices)

    def __repr__(self) -> str:
        return f"Hexahedron({self.v1}, ..., {self.v8})"


def centroid(
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> Point3D:
    """Return the centroid of a hexahedron defined by 8 vertices."""
    return Point3D(
        (v1.x + v2.x + v3.x + v4.x + v5.x + v6.x + v7.x + v8.x) / 8.0,
        (v1.y + v2.y + v3.y + v4.y + v5.y + v6.y + v7.y + v8.y) / 8.0,
        (v1.z + v2.z + v3.z + v4.z + v5.z + v6.z + v7.z + v8.z) / 8.0
    )


def volume(
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> float:
    """
    Return the volume of a hexahedron by decomposing it into 6 tetrahedra.
    This assumes the vertices are ordered as a standard 'brick' element.
    """
    # Decompose hexahedron into 6 tetrahedra sharing the same diagonal
    t1 = tet_volume(v1, v2, v4, v8)
    t2 = tet_volume(v1, v2, v8, v5)
    t3 = tet_volume(v2, v3, v4, v8)
    t4 = tet_volume(v2, v3, v8, v7)
    t5 = tet_volume(v2, v7, v8, v6)
    t6 = tet_volume(v2, v6, v8, v5)

    return abs(t1) + abs(t2) + abs(t3) + abs(t4) + abs(t5) + abs(t6)


def is_convex(
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> bool:
    """
    Check if the hexahedron is convex.
    A hexahedron is convex if all its 6 faces are convex and all vertices
    lie on the same side of each face's plane.
    """
    pts = [v1, v2, v3, v4, v5, v6, v7, v8]
    face_definitions = [
        (0, 3, 2, 1), # bottom
        (4, 5, 6, 7), # top
        (0, 1, 5, 4), # front
        (1, 2, 6, 5), # right
        (2, 3, 7, 6), # back
        (3, 0, 4, 7), # left
    ]
    
    for face in face_definitions:
        f_pts = [pts[i] for i in face]
        ref_idx = next(i for i in range(8) if i not in face)
        ref_sign = orientation_sign(f_pts[0], f_pts[1], f_pts[2], pts[ref_idx])
        if ref_sign == 0:
            for i in range(8):
                if i not in face:
                    ref_sign = orientation_sign(f_pts[0], f_pts[1], f_pts[2], pts[i])
                    if ref_sign != 0: break
        if ref_sign == 0: continue
        for i in range(8):
            if i not in face:
                s = orientation_sign(f_pts[0], f_pts[1], f_pts[2], pts[i])
                if s != 0 and s != ref_sign: return False
    return True


def contains_point(
    p: Point3D, 
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> bool:
    """
    Check if point p is inside the hexahedron.
    Assumes the hexahedron is convex.
    """
    pts = [v1, v2, v3, v4, v5, v6, v7, v8]
    face_definitions = [
        (0, 3, 2, 1), # bottom
        (4, 5, 6, 7), # top
        (0, 1, 5, 4), # front
        (1, 2, 6, 5), # right
        (2, 3, 7, 6), # back
        (3, 0, 4, 7), # left
    ]
    
    for face in face_definitions:
        f_pts = [pts[i] for i in face]
        # Reference point: pick first vertex not in face
        ref_idx = next(i for i in range(8) if i not in face)
        ref_sign = orientation_sign(f_pts[0], f_pts[1], f_pts[2], pts[ref_idx])
        
        if ref_sign == 0:
            for i in range(8):
                if i not in face:
                    ref_sign = orientation_sign(f_pts[0], f_pts[1], f_pts[2], pts[i])
                    if ref_sign != 0: break
        
        if ref_sign == 0: continue # Degenerate face or hex
        
        p_sign = orientation_sign(f_pts[0], f_pts[1], f_pts[2], p)
        if p_sign != 0 and p_sign != ref_sign:
            return False
    return True


def faces(
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> Tuple[Tuple[Point3D, Point3D, Point3D, Point3D], ...]:
    """
    Return the 6 faces of the hexahedron. 
    Each face is returned as a tuple of 4 points in counter-clockwise order when viewed from outside.
    """
    pts = [v1, v2, v3, v4, v5, v6, v7, v8]
    face_definitions = [
        (0, 3, 2, 1), # bottom (v1, v4, v3, v2)
        (4, 5, 6, 7), # top (v5, v6, v7, v8)
        (0, 1, 5, 4), # front (v1, v2, v6, v5)
        (1, 2, 6, 5), # right (v2, v3, v7, v6)
        (2, 3, 7, 6), # back (v3, v4, v8, v7)
        (3, 0, 4, 7), # left (v4, v1, v5, v8)
    ]
    
    return tuple(tuple(pts[i] for i in face) for face in face_definitions)


def edges(
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> Tuple[Tuple[Point3D, Point3D], ...]:
    """Return the 12 edges of the hexahedron."""
    pts = [v1, v2, v3, v4, v5, v6, v7, v8]
    edge_definitions = [
        (0, 1), (1, 2), (2, 3), (3, 0), # bottom
        (4, 5), (5, 6), (6, 7), (7, 4), # top
        (0, 4), (1, 5), (2, 6), (3, 7), # vertical
    ]
    return tuple(tuple(pts[i] for i in edge) for edge in edge_definitions)


def min_sphere(
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> Sphere:
    """Return the minimum bounding sphere that contains all 8 points of the hexahedron."""
    points = [v1, v2, v3, v4, v5, v6, v7, v8]
    candidates: list[Sphere] = []
    for i in range(8):
        for j in range(i + 1, 8):
            s = from_two_points(points[i], points[j])
            if all(s.contains_point(p) for p in points): candidates.append(s)
    for i in range(8):
        for j in range(i + 1, 8):
            for k in range(j + 1, 8):
                s = from_three_points(points[i], points[j], points[k])
                if all(s.contains_point(p) for p in points): candidates.append(s)
    for i in range(8):
        for j in range(i + 1, 8):
            for k in range(j + 1, 8):
                for l in range(k + 1, 8):
                    s = from_four_points(points[i], points[j], points[k], points[l])
                    if all(s.contains_point(p) for p in points): candidates.append(s)
    if not candidates: return from_four_points(v1, v2, v3, v5)
    return min(candidates, key=lambda s: s.radius)


def barycentric_coords(
    p: Point3D, 
    v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D, 
    v5: Point3D, v6: Point3D, v7: Point3D, v8: Point3D
) -> Tuple[float, float, float]:
    """
    Return the trilinear coordinates (u, v, w) of point p with respect to hexahedron (v1...v8).
    Coordinates (u, v, w) are in range [0, 1] if p is inside.
    Uses Newton-Raphson iteration.
    """
    u, v, w = 0.5, 0.5, 0.5
    pts = [v1, v2, v3, v4, v5, v6, v7, v8]
    for _ in range(10):
        # Shape functions
        N = [
            (1-u)*(1-v)*(1-w), u*(1-v)*(1-w), u*v*(1-w), (1-u)*v*(1-w),
            (1-u)*(1-v)*w, u*(1-v)*w, u*v*w, (1-u)*v*w
        ]
        f = [0.0, 0.0, 0.0]
        for i in range(8):
            f[0] += N[i] * pts[i].x
            f[1] += N[i] * pts[i].y
            f[2] += N[i] * pts[i].z
        f[0] -= p.x; f[1] -= p.y; f[2] -= p.z

        # Derivatives
        dN_du = [-(1-v)*(1-w), (1-v)*(1-w), v*(1-w), -v*(1-w), -(1-v)*w, (1-v)*w, v*w, -v*w]
        dN_dv = [-(1-u)*(1-w), -u*(1-w), u*(1-w), (1-u)*(1-w), -(1-u)*w, -u*w, u*w, (1-u)*w]
        dN_dw = [-(1-u)*(1-v), -u*(1-v), -u*v, -(1-u)*v, (1-u)*(1-v), u*(1-v), u*v, (1-u)*v]
        
        J = [[0.0]*3 for _ in range(3)]
        for i in range(8):
            J[0][0] += dN_du[i]*pts[i].x; J[0][1] += dN_dv[i]*pts[i].x; J[0][2] += dN_dw[i]*pts[i].x
            J[1][0] += dN_du[i]*pts[i].y; J[1][1] += dN_dv[i]*pts[i].y; J[1][2] += dN_dw[i]*pts[i].y
            J[2][0] += dN_du[i]*pts[i].z; J[2][1] += dN_dv[i]*pts[i].z; J[2][2] += dN_dw[i]*pts[i].z
            
        det_j = J[0][0]*(J[1][1]*J[2][2] - J[1][2]*J[2][1]) - \
                J[0][1]*(J[1][0]*J[2][2] - J[1][2]*J[2][0]) + \
                J[0][2]*(J[1][0]*J[2][1] - J[1][1]*J[2][0])
        
        if abs(det_j) < 1e-12: break
        
        invJ = [[0.0]*3 for _ in range(3)]
        invJ[0][0] = (J[1][1]*J[2][2] - J[1][2]*J[2][1]) / det_j
        invJ[0][1] = (J[0][2]*J[2][1] - J[0][1]*J[2][2]) / det_j
        invJ[0][2] = (J[0][1]*J[1][2] - J[0][2]*J[1][1]) / det_j
        # ... just solve directly instead of full inverse
        du = invJ[0][0]*(-f[0]) + invJ[0][1]*(-f[1]) + invJ[0][2]*(-f[2])
        # Re-calc for v, w
        dv = ((J[1][2]*J[2][0] - J[1][0]*J[2][2]) / det_j)*(-f[0]) + \
             ((J[0][0]*J[2][2] - J[0][2]*J[2][0]) / det_j)*(-f[1]) + \
             ((J[0][2]*J[1][0] - J[0][0]*J[1][2]) / det_j)*(-f[2])
        dw = ((J[1][0]*J[2][1] - J[1][1]*J[2][0]) / det_j)*(-f[0]) + \
             ((J[0][1]*J[2][0] - J[0][0]*J[2][1]) / det_j)*(-f[1]) + \
             ((J[0][0]*J[1][1] - J[0][1]*J[1][0]) / det_j)*(-f[2])
        
        u += du; v += dv; w += dw
        if abs(du) < 1e-9 and abs(dv) < 1e-9 and abs(dw) < 1e-9: break
    return u, v, w


__all__ = [
    "Hexahedron",
    "centroid",
    "volume",
    "is_convex",
    "contains_point",
    "faces",
    "edges",
    "min_sphere",
    "barycentric_coords",
]
