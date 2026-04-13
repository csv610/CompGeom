from __future__ import annotations
import math
from typing import List, Tuple, Union, Optional

from compgeom.kernel import Point2D, Point3D

def tri_tri_intersect(tri1_pts: List[Union[Point2D, Point3D]], tri2_pts: List[Union[Point2D, Point3D]], epsilon: float = 1e-9) -> bool:
    """
    Robust triangle-triangle intersection test using Moller's algorithm.
    """
    def get_coords(p):
        return [p.x, p.y, getattr(p, "z", 0.0)]

    v1 = [get_coords(p) for p in tri1_pts]
    v2 = [get_coords(p) for p in tri2_pts]

    def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    def cross(a, b):
        return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    def sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

    # Plane of triangle 2
    e2_1 = sub(v2[1], v2[0]); e2_2 = sub(v2[2], v2[0])
    n2 = cross(e2_1, e2_2); d2 = -dot(n2, v2[0])
    dist1 = [dot(n2, v) + d2 for v in v1]
    if all(d > epsilon for d in dist1) or all(d < -epsilon for d in dist1): return False

    # Plane of triangle 1
    e1_1 = sub(v1[1], v1[0]); e1_2 = sub(v1[2], v1[0])
    n1 = cross(e1_1, e1_2); d1 = -dot(n1, v1[0])
    dist2 = [dot(n1, v) + d1 for v in v2]
    if all(d > epsilon for d in dist2) or all(d < -epsilon for d in dist2): return False

    if all(abs(d) < epsilon for d in dist1):
        return tri_tri_coplanar_intersect(v1, v2, n1, epsilon)

    d_line = cross(n1, n2)
    def get_intervals(v, dists):
        projections = [dot(d_line, p) for p in v]
        s = [d > epsilon for d in dists]
        idx = s.index(True) if sum(s) == 1 else [d < -epsilon for d in dists].index(True)
        idx1, idx2 = (idx + 1) % 3, (idx + 2) % 3
        t1 = projections[idx] + (projections[idx1] - projections[idx]) * (dists[idx] / (dists[idx] - dists[idx1]))
        t2 = projections[idx] + (projections[idx2] - projections[idx]) * (dists[idx] / (dists[idx] - dists[idx2]))
        return sorted((t1, t2))

    t1_min, t1_max = get_intervals(v1, dist1)
    t2_min, t2_max = get_intervals(v2, dist2)
    return t1_max >= t2_min - epsilon and t2_max >= t1_min - epsilon

def tri_tri_coplanar_intersect(v1, v2, normal, epsilon=1e-9):
    """2D intersection check for coplanar triangles using PANG2 algorithm."""
    abs_n = [abs(x) for x in normal]
    if abs_n[0] > abs_n[1] and abs_n[0] > abs_n[2]:
        p1, p2 = [(p[1], p[2]) for p in v1], [(p[1], p[2]) for p in v2]
    elif abs_n[1] > abs_n[2]:
        p1, p2 = [(p[0], p[2]) for p in v1], [(p[0], p[2]) for p in v2]
    else:
        p1, p2 = [(p[0], p[1]) for p in v1], [(p[0], p[1]) for p in v2]

    def check_mapped(triA, triB):
        v0, va, vb = triA[0], triA[1], triA[2]
        dx1, dy1 = va[0] - v0[0], va[1] - v0[1]
        dx2, dy2 = vb[0] - v0[0], vb[1] - v0[1]
        det = dx1 * dy2 - dy1 * dx2
        if abs(det) < epsilon: return False
        inv_det = 1.0 / det
        A00, A01 = dy2 * inv_det, -dx2 * inv_det
        A10, A11 = -dy1 * inv_det, dx1 * inv_det
        X = []
        for u in triB:
            dux, duy = u[0] - v0[0], u[1] - v0[1]
            X.append((A00 * dux + A01 * duy, A10 * dux + A11 * duy))
        def sign(p_val): return 1 if p_val >= -epsilon else 0
        for line_idx in range(3):
            p_vals, q_vals = [], []
            for x, y in X:
                if line_idx == 0: p_vals.append(y); q_vals.append(x)
                elif line_idx == 1: p_vals.append(x); q_vals.append(y)
                else: p_vals.append(1.0 - x - y); q_vals.append((1.0 - x + y) / 2.0)
            if all(sign(p) == 0 for p in p_vals): return False
            for i in range(3):
                j = (i + 1) % 3
                if sign(p_vals[i]) != sign(p_vals[j]):
                    denom = p_vals[j] - p_vals[i]
                    if abs(denom) > 1e-12:
                        q_int = (p_vals[j] * q_vals[i] - p_vals[i] * q_vals[j]) / denom
                        if -epsilon <= q_int <= 1.0 + epsilon: return True
        if sign(X[0][1]) == 1 and sign(X[0][0]) == 1 and sign(1.0 - X[0][0] - X[0][1]) == 1: return True
        return None

    res = check_mapped(p2, p1)
    if res is not None: return res
    res = check_mapped(p1, p2)
    if res is not None: return res
    return False

def tri_tetra_intersect(tri_v: Tuple[Point3D, Point3D, Point3D], tetra_v: Tuple[Point3D, Point3D, Point3D, Point3D], epsilon: float = 1e-9) -> bool:
    """Robust Triangle-Tetrahedron intersection test using SAT."""
    from compgeom.kernel.tetrahedron import contains_point
    for p in tri_v:
        if contains_point(tetra_v[0], tetra_v[1], tetra_v[2], tetra_v[3], p): return True
    
    def get_coords(p): return [p.x, p.y, p.z]
    p1, p2 = [get_coords(p) for p in tri_v], [get_coords(p) for p in tetra_v]
    def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    def cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    def sub(a, b): return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]
    
    edges1 = [sub(p1[1], p1[0]), sub(p1[2], p1[1]), sub(p1[0], p1[2])]
    edges2 = [sub(p2[1], p2[0]), sub(p2[0], p2[2]), sub(p2[0], p2[3]), sub(p2[1], p2[2]), sub(p2[1], p2[3]), sub(p2[2], p2[3])]
    n1 = cross(edges1[0], edges1[1])
    n2_faces = [cross(sub(p2[1], p2[0]), sub(p2[2], p2[0])), cross(sub(p2[1], p2[0]), sub(p2[3], p2[0])), cross(sub(p2[2], p2[0]), sub(p2[3], p2[0])), cross(sub(p2[2], p2[1]), sub(p2[3], p2[1]))]
    
    for axis in [n1] + n2_faces + [cross(e1, e2) for e1 in edges1 for e2 in edges2]:
        if dot(axis, axis) < 1e-12: continue
        min1 = max1 = dot(axis, p1[0])
        for i in range(1, 3):
            val = dot(axis, p1[i]); min1, max1 = min(min1, val), max(max1, val)
        min2 = max2 = dot(axis, p2[0])
        for i in range(1, 4):
            val = dot(axis, p2[i]); min2, max2 = min(min2, val), max(max2, val)
        if max1 < min2 - epsilon or max2 < min1 - epsilon: return False
    return True

def tri_hex_intersect(tri_v: Tuple[Point3D, Point3D, Point3D], hex_v: Tuple[Point3D, ...], epsilon: float = 1e-9) -> bool:
    """Robust Triangle-Hexahedron intersection test by decomposition."""
    t_defs = [(0, 1, 2, 5), (0, 2, 3, 7), (0, 5, 7, 4), (2, 5, 7, 6), (0, 2, 5, 7)]
    for t_idx in t_defs:
        if tri_tetra_intersect(tri_v, tuple(hex_v[i] for i in t_idx), epsilon): return True
    return False

def box_box_intersect_3d(min1: Tuple[float, float, float], max1: Tuple[float, float, float], 
                        min2: Tuple[float, float, float], max2: Tuple[float, float, float]) -> bool:
    return not (min1[0] > max2[0] or min2[0] > max1[0] or
                min1[1] > max2[1] or min2[1] > max1[1] or
                min1[2] > max2[2] or min2[2] > max1[2])

def box_box_intersect_2d(min1: Tuple[float, float], max1: Tuple[float, float], 
                        min2: Tuple[float, float], max2: Tuple[float, float]) -> bool:
    return not (min1[0] > max2[0] or min2[0] > max1[0] or
                min1[1] > max2[1] or min2[1] > max1[1])
