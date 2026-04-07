from __future__ import annotations

from typing import List, Tuple

import numpy as np
from scipy.spatial import ConvexHull, Delaunay

from compgeom.kernel import Point3D, distance_3d
from compgeom.kernel.sphere import from_four_points

__all__ = ["find_largest_empty_sphere"]


def find_largest_empty_sphere(points: List[Point3D]) -> Tuple[Point3D, float]:

    if len(points) < 4:
        if len(points) == 2:
            p1, p2 = points
            center = Point3D(
                (p1.x + p2.x) / 2.0,
                (p1.y + p2.y) / 2.0,
                (getattr(p1, "z", 0.0) + getattr(p2, "z", 0.0)) / 2.0,
            )
            return center, distance_3d(p1, p2) / 2.0
        return Point3D(0, 0, 0), 0.0

    pts_array = np.array([[p.x, p.y, getattr(p, "z", 0.0)] for p in points])
    delaunay = Delaunay(pts_array)

    max_radius = -1.0
    best_center = None

    # 1. Check circumcenters of Delaunay tetrahedra
    for simplex in delaunay.simplices:
        p1, p2, p3, p4 = [points[i] for i in simplex]
        sphere = from_four_points(p1, p2, p3, p4)
        center = sphere.center

        # Check if center is inside the convex hull
        if delaunay.find_simplex(np.array([center.x, center.y, center.z])) >= 0:
            # Use actual radius calculation for safety
            r = min(distance_3d(center, p) for p in [p1, p2, p3, p4])
            if r > max_radius:
                max_radius = r
                best_center = center

    # 2. Check centers of convex hull faces
    hull = ConvexHull(pts_array)
    for simplex in hull.simplices:
        p1, p2, p3 = [points[i] for i in simplex]
        center = Point3D(
            (p1.x + p2.x + p3.x) / 3.0,
            (p1.y + p2.y + p3.y) / 3.0,
            (getattr(p1, "z", 0) + getattr(p2, "z", 0) + getattr(p3, "z", 0)) / 3.0,
        )

        # Find min distance to any point
        # (Using a simple loop since N usually isn't huge in this context; KDTree could be used for huge N)
        min_d = min(distance_3d(center, p) for p in points)
        if min_d > max_radius:
            max_radius = min_d
            best_center = center

    # 3. Check midpoints of convex hull edges
    edges = set()
    for simplex in hull.simplices:
        for i in range(3):
            j = (i + 1) % 3
            u, v = simplex[i], simplex[j]
            edges.add((min(u, v), max(u, v)))

    for u, v in edges:
        p1, p2 = points[u], points[v]
        mid = Point3D(
            (p1.x + p2.x) / 2.0,
            (p1.y + p2.y) / 2.0,
            (getattr(p1, "z", 0) + getattr(p2, "z", 0)) / 2.0,
        )
        min_d = min(distance_3d(mid, p) for p in points)
        if min_d > max_radius:
            max_radius = min_d
            best_center = mid

    if best_center is None:
        return Point3D(0, 0, 0), 0.0

    return best_center, max_radius
