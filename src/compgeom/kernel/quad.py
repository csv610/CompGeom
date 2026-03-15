from __future__ import annotations
import math
from typing import TYPE_CHECKING, Tuple, List, Union

from .point import Point2D, Point3D
from .circle import Circle2D, from_two_points, from_three_points, incircle_sign
from .math_utils import (
    EPSILON, 
    cross_product,
)
from .triangle import area as triangle_area
from .tetrahedron import orientation_sign


def min_circle(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Circle2D:
    """Return the minimum bounding circle that contains all 4 points of the quadrilateral."""
    points = [p1, p2, p3, p4]
    
    candidates: list[Circle2D] = []
    
    # 1. Check circles with 2 points as diameter
    for i in range(4):
        for j in range(i + 1, 4):
            c, r = from_two_points(points[i], points[j])
            circle = Circle2D(c, r)
            if all(circle.contains_point(p) for p in points):
                candidates.append(circle)
                
    # 2. Check circles with 3 points as circumcircle
    for i in range(4):
        for j in range(i + 1, 4):
            for k in range(j + 1, 4):
                c, r = from_three_points(points[i], points[j], points[k])
                circle = Circle2D(c, r)
                if all(circle.contains_point(p) for p in points):
                    candidates.append(circle)
                    
    if not candidates:
        # Fallback: this case should technically not be reached for 4 points
        # unless they are numerical edge cases.
        c, r = from_three_points(p1, p2, p3)
        return Circle2D(c, r)
        
    return min(candidates, key=lambda c: c.radius)


def area(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> float:
    """Return the area of a quadrilateral (p1, p2, p3, p4)."""
    # Using the sum of two triangles (p1, p2, p3) and (p1, p3, p4)
    return abs(triangle_area(p1, p2, p3)) + abs(triangle_area(p1, p3, p4))


def is_convex(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> bool:
    """Check if quadrilateral (p1, p2, p3, p4) is convex."""
    # A quad is convex if all internal angles are < 180 degrees.
    # This is true if all cross products of consecutive edges have the same sign.
    cp1 = cross_product(p1, p2, p3)
    cp2 = cross_product(p2, p3, p4)
    cp3 = cross_product(p3, p4, p1)
    cp4 = cross_product(p4, p1, p2)
    
    return (
        (cp1 > EPSILON and cp2 > EPSILON and cp3 > EPSILON and cp4 > EPSILON) or
        (cp1 < -EPSILON and cp2 < -EPSILON and cp3 < -EPSILON and cp4 < -EPSILON)
    )


def split_to_triangles(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> list[tuple[Point2D, Point2D, Point2D]]:
    """Split a quadrilateral into two triangles."""
    # Standard split into two triangles
    return [(p1, p2, p3), (p1, p3, p4)]


def centroid(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Point2D:
    """Return the centroid of a quadrilateral."""
    return Point2D(
        (p1.x + p2.x + p3.x + p4.x) / 4.0,
        (p1.y + p2.y + p3.y + p4.y) / 4.0
    )


def is_planar(p1: Point2D | Point3D, p2: Point2D | Point3D, p3: Point2D | Point3D, p4: Point2D | Point3D) -> bool:
    """Check if quadrilateral (p1, p2, p3, p4) is planar."""
    if all(isinstance(p, Point2D) for p in [p1, p2, p3, p4]):
        return True
    
    # Using 3D orientation sign:
    # Converting any Point2D to Point3D if mixed
    pts = []
    for p in [p1, p2, p3, p4]:
        if isinstance(p, Point3D):
            pts.append(p)
        else:
            pts.append(Point3D(p.x, p.y, 0.0))
            
    return orientation_sign(pts[0], pts[1], pts[2], pts[3]) == 0


def is_cyclic(p1: Point2D | Point3D, p2: Point2D | Point3D, p3: Point2D | Point3D, p4: Point2D | Point3D) -> bool:
    """Check if quadrilateral (p1, p2, p3, p4) is cyclic (all vertices on the same circle)."""
    if not is_planar(p1, p2, p3, p4):
        return False
    
    if all(isinstance(p, Point2D) for p in [p1, p2, p3, p4]):
        # Use robust incircle predicate for 2D
        return incircle_sign(p1, p2, p3, p4) == 0

    # For 3D (or mixed), use Ptolemy's Theorem: AC * BD = AB * CD + BC * AD (for cyclic order)
    # We check all three possible combinations of products for any vertex ordering.
    d12 = p1.distance_to(p2)
    d13 = p1.distance_to(p3)
    d14 = p1.distance_to(p4)
    d23 = p2.distance_to(p3)
    d24 = p2.distance_to(p4)
    d34 = p3.distance_to(p4)
    
    p_a = d13 * d24
    p_b = d12 * d34
    p_c = d23 * d14
    
    # Ptolemy's equality AC*BD = AB*CD + BC*AD holds if A,B,C,D are concyclic in some order.
    # Equality also holds for collinear points, which are considered concyclic on a degenerate circle.
    return (math.isclose(p_a, p_b + p_c, abs_tol=EPSILON) or
            math.isclose(p_b, p_a + p_c, abs_tol=EPSILON) or
            math.isclose(p_c, p_a + p_b, abs_tol=EPSILON))


def barycentric_coords(p: Point2D, p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Tuple[float, float]:
    """
    Return the bilinear coordinates (u, v) of point p with respect to quadrilateral (p1, p2, p3, p4).
    The coordinates (u, v) are in range [0, 1] if p is inside the quad.
    P(u, v) = (1-u)(1-v)p1 + u(1-v)p2 + uvp3 + (1-u)vp4
    """
    # Using Newton-Raphson to solve for u, v
    u, v = 0.5, 0.5
    for _ in range(10):
        # P(u, v)
        f_uv_x = (1-u)*(1-v)*p1.x + u*(1-v)*p2.x + u*v*p3.x + (1-u)*v*p4.x - p.x
        f_uv_y = (1-u)*(1-v)*p1.y + u*(1-v)*p2.y + u*v*p3.y + (1-u)*v*p4.y - p.y
        
        # Jacobian entries
        # df/du
        df_du_x = -(1-v)*p1.x + (1-v)*p2.x + v*p3.x - v*p4.x
        df_du_y = -(1-v)*p1.y + (1-v)*p2.y + v*p3.y - v*p4.y
        # df/dv
        df_dv_x = -(1-u)*p1.x - u*p2.x + u*p3.x + (1-u)*p4.x
        df_dv_y = -(1-u)*p1.y - u*p2.y + u*p3.y + (1-u)*p4.y
        
        det_j = df_du_x * df_dv_y - df_dv_x * df_du_y
        if abs(det_j) < 1e-12:
            break
            
        du = (f_uv_y * df_dv_x - f_uv_x * df_dv_y) / det_j
        dv = (f_uv_x * df_du_y - f_uv_y * df_du_x) / det_j
        
        u += du
        v += dv
        
        if abs(du) < 1e-9 and abs(dv) < 1e-9:
            break
            
    return u, v


__all__ = [
    "min_circle",
    "area",
    "is_convex",
    "split_to_triangles",
    "centroid",
    "is_planar",
    "is_cyclic",
    "barycentric_coords",
]
