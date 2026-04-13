from __future__ import annotations
import math
from typing import Tuple, Optional, List, TYPE_CHECKING

from compgeom.kernel import Point2D, Point3D

def ray_triangle_intersect(origin: Tuple[float, float, float], direction: Tuple[float, float, float],
                         v0: Tuple[float, float, float], v1: Tuple[float, float, float], v2: Tuple[float, float, float],
                         epsilon: float = 1e-8) -> Optional[Tuple[float, float, float]]:
    """Möller–Trumbore ray-triangle intersection. Returns (t, u, v)."""
    e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
    e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
    h = (direction[1]*e2[2]-direction[2]*e2[1], direction[2]*e2[0]-direction[0]*e2[2], direction[0]*e2[1]-direction[1]*e2[0])
    a = e1[0]*h[0] + e1[1]*h[1] + e1[2]*h[2]
    if -epsilon < a < epsilon: return None
    f = 1.0 / a
    s = (origin[0]-v0[0], origin[1]-v0[1], origin[2]-v0[2])
    u = f * (s[0]*h[0] + s[1]*h[1] + s[2]*h[2])
    if u < -epsilon or u > 1.0 + epsilon: return None
    q = (s[1]*e1[2]-s[2]*e1[1], s[2]*e1[0]-s[0]*e1[2], s[0]*e1[1]-s[1]*e1[0])
    v = f * (direction[0]*q[0] + direction[1]*q[1] + direction[2]*q[2])
    if v < -epsilon or u + v > 1.0 + epsilon: return None
    t = f * (e1[0]*q[0] + e1[1]*q[1] + e1[2]*q[2]) # Wait, Möller-Trumbore t is edge2.dot(q). Let's fix.
    t = f * (e2[0]*q[0] + e2[1]*q[1] + e2[2]*q[2])
    return (t, u, v) if t > epsilon else None

def ray_sphere_intersect(origin: Tuple[float, float, float], direction: Tuple[float, float, float],
                        center: Tuple[float, float, float], radius: float) -> Optional[Tuple[float, float]]:
    """Ray-sphere intersection. Returns (t1, t2)."""
    oc = (origin[0]-center[0], origin[1]-center[1], origin[2]-center[2])
    b = 2.0 * (oc[0]*direction[0] + oc[1]*direction[1] + oc[2]*direction[2])
    c = (oc[0]**2 + oc[1]**2 + oc[2]**2) - radius**2
    disc = b*b - 4*c
    if disc < 0: return None
    t1 = (-b - math.sqrt(disc)) / 2.0
    t2 = (-b + math.sqrt(disc)) / 2.0
    return (max(0.0, t1), t2) if t2 >= 0 else None

def ray_aabb_intersect_3d(origin: Tuple[float, float, float], direction: Tuple[float, float, float],
                        bmin: Tuple[float, float, float], bmax: Tuple[float, float, float]) -> Optional[Tuple[float, float]]:
    """Ray-AABB intersection in 3D. Returns (t_min, t_max)."""
    tmin, tmax = -float('inf'), float('inf')
    for i in range(3):
        if abs(direction[i]) < 1e-12:
            if origin[i] < bmin[i] or origin[i] > bmax[i]: return None
        else:
            inv_d = 1.0 / direction[i]
            t1 = (bmin[i] - origin[i]) * inv_d
            t2 = (bmax[i] - origin[i]) * inv_d
            tmin = max(tmin, min(t1, t2))
            tmax = min(tmax, max(t1, t2))
    return (tmin, tmax) if tmax >= max(0.0, tmin) else None

def ray_plane_intersect(origin: Tuple[float, float, float], direction: Tuple[float, float, float],
                       plane_point: Tuple[float, float, float], plane_normal: Tuple[float, float, float]) -> Optional[float]:
    """Ray-plane intersection. Returns t."""
    denom = direction[0]*plane_normal[0] + direction[1]*plane_normal[1] + direction[2]*plane_normal[2]
    if abs(denom) < 1e-12: return None
    t = ((plane_point[0]-origin[0])*plane_normal[0] + (plane_point[1]-origin[1])*plane_normal[1] + (plane_point[2]-origin[2])*plane_normal[2]) / denom
    return t if t >= 0 else None
