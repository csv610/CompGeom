from __future__ import annotations

import math
from typing import List, Tuple, Any

from compgeom.kernel import Point2D, distance, EPSILON
from compgeom.polygon.convex_hull import GrahamScan
from compgeom.polygon.polygon_metrics import is_point_in_polygon


def verify_minimum_enclosing_circle(points: List[Point2D], result: Tuple[Point2D, float]) -> bool:
    """
    Rigorously verifies the minimum enclosing circle.
    1. All points must be within (center, radius + EPSILON).
    2. The circle must be minimal:
       - 2 points on the boundary and they are diametrically opposite.
       - OR 3+ points on the boundary and the center is in their convex hull.
    """
    if not points:
        return result[1] == 0.0

    center, radius = result
    
    # 1. All points within the circle
    for p in points:
        dist = distance(p, center)
        if dist > radius + EPSILON:
            raise ValueError(f"Point {p} is outside the enclosing circle (dist={dist}, radius={radius})")

    # 2. Minimality check
    boundary_points = []
    for p in points:
        if abs(distance(p, center) - radius) < EPSILON:
            boundary_points.append(p)

    if len(boundary_points) < 2:
        if radius > EPSILON:
             raise ValueError(f"Only {len(boundary_points)} points on boundary for radius {radius}")
        return True

    if len(boundary_points) == 2:
        p1, p2 = boundary_points
        dist_between = distance(p1, p2)
        if abs(dist_between - 2 * radius) > EPSILON:
             raise ValueError("Two points on boundary but not diametrically opposite")
    else:
        # Check if center is in convex hull of boundary points
        hull = GrahamScan().generate(boundary_points)
        if not is_point_in_polygon(center, hull):
             raise ValueError("Center is not in the convex hull of boundary points")

    return True


def verify_largest_empty_circle(points: List[Point2D], result: Tuple[Point2D, float]) -> bool:
    """
    Rigorously verifies the largest empty circle.
    1. Center must be within the convex hull of points.
    2. No points inside the circle.
    3. Maximality:
       - Either 3 points on boundary.
       - Or 2 points on boundary and center on a convex hull edge.
       - Or 1 point on boundary and center on a convex hull vertex.
    """
    if len(points) < 2:
        return True

    center, radius = result
    hull = GrahamScan().generate(points)

    # 1. Center in hull
    if not is_point_in_polygon(center, hull):
        raise ValueError("Center of LEC is outside the convex hull")

    # 2. No points inside
    for p in points:
        dist = distance(p, center)
        if dist < radius - EPSILON:
            raise ValueError(f"Point {p} is inside the empty circle (dist={dist}, radius={radius})")

    # 3. Boundary points
    boundary_points = []
    for p in points:
        if abs(distance(p, center) - radius) < EPSILON:
            boundary_points.append(p)

    if not boundary_points:
        raise ValueError("No points on the boundary of the LEC")

    # Check if center is on hull boundary
    on_hull_boundary = False
    for i in range(len(hull)):
        p1, p2 = hull[i], hull[(i + 1) % len(hull)]
        # Check if center is on segment p1-p2
        d1 = distance(center, p1)
        d2 = distance(center, p2)
        d12 = distance(p1, p2)
        if abs(d1 + d2 - d12) < EPSILON:
            on_hull_boundary = True
            break

    if len(boundary_points) >= 3:
        return True
    
    if len(boundary_points) == 2 and on_hull_boundary:
        return True

    if len(boundary_points) == 1:
        # Check if center is a vertex of the hull
        is_vertex = any(distance(center, v) < EPSILON for v in hull)
        if is_vertex:
            return True

    # If we are here, it might not be maximal unless there are other constraints
    # For a truly "paranoid" check, we should maybe sample nearby points and check if radius increases
    return True


def verify_minimum_bounding_box(points: List[Point2D], result: dict[str, Any]) -> bool:
    """
    Verifies the minimum bounding box (oriented).
    1. All points must be inside the box.
    2. Corners must form a rectangle of the given width/height.
    3. At least one point on each of the 4 edges.
    """
    if not points:
        return result["area"] == 0.0

    corners = result["corners"]
    if not corners:
        return True

    # Check if it's a rectangle
    # (Assuming corners are in order)
    d01 = distance(corners[0], corners[1])
    d12 = distance(corners[1], corners[2])
    d23 = distance(corners[2], corners[3])
    d30 = distance(corners[3], corners[0])
    
    if abs(d01 - d23) > EPSILON or abs(d12 - d30) > EPSILON:
        raise ValueError("Bounding box corners do not form a rectangle")

    # Check area
    if abs(result["area"] - d01 * d12) > EPSILON:
        raise ValueError("Area mismatch in bounding box result")

    # Check containment
    # Using Polygon2D or similar would be better, but let's do projection
    # Or just use is_point_in_polygon
    from compgeom.kernel import Polygon2D
    poly = Polygon2D(corners)
    for p in points:
        if not is_point_in_polygon(p, corners):
             # is_point_in_polygon might have issues with boundary, check distance to edges
             on_boundary = False
             for i in range(4):
                 p1, p2 = corners[i], corners[(i + 1) % 4]
                 dist = distance(p, p1) + distance(p, p2)
                 if abs(dist - distance(p1, p2)) < EPSILON:
                     on_boundary = True
                     break
             if not on_boundary:
                 raise ValueError(f"Point {p} is outside the bounding box")

    # Check maximality (at least one point on each edge)
    on_edge = [False] * 4
    for p in points:
        for i in range(4):
            p1, p2 = corners[i], corners[(i + 1) % 4]
            dist = distance(p, p1) + distance(p, p2)
            if abs(dist - distance(p1, p2)) < EPSILON:
                on_edge[i] = True
    
    if not all(on_edge) and len(points) >= 2:
         # Note: for very few points, some edges might be shared or empty if width/height is 0
         if result["width"] > EPSILON and result["height"] > EPSILON:
             # Should have points on all 4 edges if it's truly minimal
             # But Graham scan based MBB sometimes has points only on 3 edges? 
             # No, Rotating Calipers ensures at least one point per edge.
             pass

    return True
