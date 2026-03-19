"""Distance, intersection, and enclosing-shape algorithms."""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, List, Optional, Tuple, Union

from compgeom.kernel import (
    EPSILON,
    Point2D,
    cross_product,
    dist_point_to_segment,
    dot_product,
    triangle_circumcenter,
    is_on_segment,
    length,
    sub,
    distance,
    get_circle_three_points,
    get_circle_two_points,
    orientation as math_orientation,
    signed_area_twice,
    support,
)
from compgeom.polygon.convex_hull import GrahamScan
from compgeom.polygon.polygon_metrics import is_point_in_polygon


class ClosestPair:
    """Algorithms for finding the closest pair of points in a set."""

    @staticmethod
    def divide_and_conquer(points: List[Point2D]) -> Tuple[float, Tuple[Optional[Point2D], Optional[Point2D]]]:
        """Traditional O(N log N) divide and conquer algorithm."""
        if not points:
            return float("inf"), (None, None)
        
        points_x = sorted(points, key=lambda p: p.x)
        points_y = sorted(points, key=lambda p: p.y)
        
        return ClosestPair._divide_and_conquer_recursive(points_x, points_y)

    @staticmethod
    def _divide_and_conquer_recursive(
        points_x: List[Point2D], points_y: List[Point2D]
    ) -> Tuple[float, Tuple[Optional[Point2D], Optional[Point2D]]]:
        n = len(points_x)
        if n <= 3:
            min_dist = float("inf")
            pair = (None, None)
            for i in range(n):
                for j in range(i + 1, n):
                    d = distance(points_x[i], points_x[j])
                    if d < min_dist:
                        min_dist = d
                        pair = (points_x[i], points_x[j])
            return min_dist, pair

        mid = n // 2
        mid_point = points_x[mid]

        # Better way to split points_y in O(n):
        left_set = set(points_x[:mid])
        points_y_left = [p for p in points_y if p in left_set]
        points_y_right = [p for p in points_y if p not in left_set]

        d1, pair1 = ClosestPair._divide_and_conquer_recursive(points_x[:mid], points_y_left)
        d2, pair2 = ClosestPair._divide_and_conquer_recursive(points_x[mid:], points_y_right)

        if d1 < d2:
            best_d, best_pair = d1, pair1
        else:
            best_d, best_pair = d2, pair2

        strip = [p for p in points_y if abs(p.x - mid_point.x) < best_d]

        for i in range(len(strip)):
            for j in range(i + 1, len(strip)):
                if strip[j].y - strip[i].y >= best_d:
                    break
                d = distance(strip[i], strip[j])
                if d < best_d:
                    best_d = d
                    best_pair = (strip[i], strip[j])

        return best_d, best_pair

    @staticmethod
    def grid_based_massive(
        points_iterator: Iterable[Point2D], 
        sample_size: int = 1000
    ) -> Tuple[float, Tuple[Point2D, Point2D]]:
        """
        O(N) randomized grid-based algorithm for massive datasets.
        Suitable for billions of points as it can process them in a stream.
        """
        points_list = []
        try:
            for _ in range(sample_size):
                p = next(points_iterator)
                points_list.append(p)
        except StopIteration:
            pass

        if len(points_list) < 2:
            raise ValueError("Need at least 2 points.")

        best_d, best_pair = ClosestPair.divide_and_conquer(points_list)
        
        grid: Dict[Tuple[int, int], Point2D] = {}
        
        def add_to_grid(p: Point2D, d: float):
            gx, gy = int(p.x / d), int(p.y / d)
            local_best_d = d
            local_pair = None
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    key = (gx + dx, gy + dy)
                    if key in grid:
                        other = grid[key]
                        dist = distance(p, other)
                        if dist < local_best_d:
                            local_best_d = dist
                            local_pair = (p, other)
            
            if local_pair:
                return local_best_d, local_pair
            
            grid[(gx, gy)] = p
            return d, None

        for p in points_list:
            gx, gy = int(p.x / best_d), int(p.y / best_d)
            grid[(gx, gy)] = p

        for p in points_iterator:
            new_d, new_pair = add_to_grid(p, best_d)
            if new_pair:
                best_d = new_d
                best_pair = new_pair
                
        return best_d, best_pair


class LargestEmptyCircle:
    """Finds the largest circle whose center is within the convex hull and encloses no points."""

    @staticmethod
    def find(points: List[Point2D]) -> Tuple[Point2D, float]:
        """
        Returns (center, radius) of the largest empty circle.
        Complexity: O(N log N) due to Delaunay Triangulation.
        """
        if len(points) < 3:
            if len(points) == 2:
                p1, p2 = points
                center = Point2D((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
                return center, distance(p1, p2) / 2.0
            return Point2D(0, 0), 0.0

        hull = GrahamScan().generate(points)
        from compgeom.mesh.surfmesh.trimesh.delaunay_triangulation import triangulate
        mesh = triangulate(points)
        triangles = [(mesh.vertices[f[0]], mesh.vertices[f[1]], mesh.vertices[f[2]]) for f in mesh.faces]
        
        max_radius = -1.0
        best_center = None
        
        for tri in triangles:
            a, b, c = tri
            center = triangle_circumcenter(a, b, c)
            if center is None:
                continue
                
            if is_point_in_polygon(center, hull): 
                r = distance(center, a) 
                if r > max_radius: 
                    max_radius = r 
                    best_center = center 
            else: 
                for i in range(len(hull)): 
                    p1, p2 = hull[i], hull[(i + 1) % len(hull)] 
                    from compgeom.kernel import ray_segment_intersection_2d 
                    res = ray_segment_intersection_2d(a, math.atan2(center.y - a.y, center.x - a.x), p1, p2) 
                    if res: 
                        _, hit = res 
                        r = distance(hit, a) 
                        if r > max_radius: 
                            max_radius = r 
                            best_center = hit
        
        for i in range(len(hull)):
            p1 = hull[i]
            p2 = hull[(i + 1) % len(hull)]
            mid = Point2D((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
            min_d = min(distance(mid, p) for p in points)
            if min_d > max_radius:
                max_radius = min_d
                best_center = mid

        return best_center, max_radius

    @staticmethod
    def visualize(points: List[Point2D], center: Point2D, radius: float) -> str:
        """Generates an SVG visualization of the points and the LEC."""
        all_x = [p.x for p in points] + [center.x - radius, center.x + radius]
        all_y = [p.y for p in points] + [center.y - radius, center.y + radius]
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        width, height = 800, 600
        padding = 50
        
        def tx(x):
            return padding + (x - min_x) / (max_x - min_x) * (width - 2 * padding) if max_x > min_x else padding
        def ty(y):
            return height - (padding + (y - min_y) / (max_y - min_y) * (height - 2 * padding)) if max_y > min_y else padding

        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="white" />')
        
        hull = GrahamScan().generate(points)
        hull_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in hull)
        svg.append(f'<polygon points="{hull_str}" fill="none" stroke="#ccc" stroke-dasharray="5,5" />')
        
        for p in points:
            svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="3" fill="black" />')
            
        svg.append(f'<circle cx="{tx(center.x)}" cy="{ty(center.y)}" r="{radius * (width - 2*padding) / (max_x - min_x) if max_x > min_x else 0}" fill="blue" fill-opacity="0.2" stroke="blue" stroke-width="2" />')
        svg.append(f'<circle cx="{tx(center.x)}" cy="{ty(center.y)}" r="4" fill="red" />')
        
        svg.append('</svg>')
        return "\n".join(svg)


def closest_pair(points: list[Point2D]):
    """Wrapper for ClosestPair.divide_and_conquer."""
    return ClosestPair.divide_and_conquer(points)


def do_intersect(p1: Point2D, q1: Point2D, p2: Point2D, q2: Point2D) -> bool:
    o1 = math_orientation(p1, q1, p2)
    o2 = math_orientation(p1, q1, q2)
    o3 = math_orientation(p2, q2, p1)
    o4 = math_orientation(p2, q2, q1)

    def get_sign(val):
        if abs(val) < 1e-9:
            return 0
        return 1 if val > 0 else 2

    s1, s2, s3, s4 = get_sign(o1), get_sign(o2), get_sign(o3), get_sign(o4)

    return (
        (s1 != s2 and s3 != s4)
        or (s1 == 0 and is_on_segment(p2, p1, q1))
        or (s2 == 0 and is_on_segment(q2, p1, q1))
        or (s3 == 0 and is_on_segment(p1, p2, q2))
        or (s4 == 0 and is_on_segment(q1, p2, q2))
    )


def farthest_pair(points: list[Point2D]):
    hull = GrahamScan().generate(points)
    if len(hull) == 0:
        return 0, (None, None)
    if len(hull) == 1:
        return 0, (hull[0], hull[0])
    if len(hull) == 2:
        return distance(hull[0], hull[1]), (hull[0], hull[1])

    max_distance = 0.0
    pair = (None, None)
    k = 1
    for index in range(len(hull)):
        while True:
            current_area = abs(
                cross_product(hull[index], hull[(index + 1) % len(hull)], hull[k])
            )
            next_area = abs(
                cross_product(
                    hull[index], hull[(index + 1) % len(hull)], hull[(k + 1) % len(hull)]
                )
            )
            if next_area > current_area:
                k = (k + 1) % len(hull)
            else:
                break

        d1 = distance(hull[index], hull[k])
        d2 = distance(hull[(index + 1) % len(hull)], hull[k])
        if d1 > max_distance:
            max_distance = d1
            pair = (hull[index], hull[k])
        if d2 > max_distance:
            max_distance = d2
            pair = (hull[(index + 1) % len(hull)], hull[k])

    return max_distance, pair


def welzl(points: list[Point2D], boundary: list[Point2D]):
    if not points or len(boundary) == 3:
        if not boundary:
            return Point2D(0, 0), 0
        if len(boundary) == 1:
            return boundary[0], 0
        if len(boundary) == 2:
            return get_circle_two_points(boundary[0], boundary[1])
        return get_circle_three_points(boundary[0], boundary[1], boundary[2])

    point = points.pop()
    center, radius = welzl(points, boundary)
    if distance(center, point) <= radius + 1e-9:
        points.append(point)
        return center, radius

    boundary.append(point)
    result = welzl(points, boundary)
    boundary.pop()
    points.append(point)
    return result


def minkowski_sum(poly1: list[Point2D], poly2: list[Point2D]) -> list[Point2D]:
    if not poly1 or not poly2:
        return []

    def prepare_polygon(polygon: list[Point2D]) -> list[Point2D]:
        area_twice = signed_area_twice(polygon)
        ordered = polygon if area_twice >= 0 else list(reversed(polygon))
        start_index = min(
            range(len(ordered)), key=lambda index: (ordered[index].y, ordered[index].x)
        )
        return ordered[start_index:] + ordered[:start_index]

    p1 = prepare_polygon(poly1)
    p2 = prepare_polygon(poly2)
    p1.append(p1[0])
    p2.append(p2[0])

    result: list[Point2D] = []
    i = j = 0
    n = len(p1) - 1
    m = len(p2) - 1
    while i < n or j < m:
        result.append(Point2D(p1[i % n].x + p2[j % m].x, p1[i % n].y + p2[j % m].y))
        if i < n and j < m:
            angle1 = (
                math.atan2(p1[i + 1].y - p1[i].y, p1[i + 1].x - p1[i].x) % (2 * math.pi)
            )
            angle2 = (
                math.atan2(p2[j + 1].y - p2[j].y, p2[j + 1].x - p2[j].x) % (2 * math.pi)
            )
            if angle1 < angle2:
                i += 1
            elif angle1 > angle2:
                j += 1
            else:
                i += 1
                j += 1
        elif i < n:
            i += 1
        else:
            j += 1
    return result


__all__ = [
    "ClosestPair",
    "LargestEmptyCircle",
    "LargestEmptySphere",
    "LargestEmptyOrientedBox",
    "LargestEmptyOrientedEllipsoid",
    "LargestEmptyOrientedRectangle",
    "LargestEmptyOrientedEllipse",
    "closest_pair",
    "do_intersect",
    "farthest_pair",
    "get_circle_three_points",
    "get_circle_two_points",
    "minkowski_sum",
    "support",
    "welzl",
]


class LargestEmptySphere:
    """Finds the largest sphere whose center is within the 3D convex hull and encloses no points."""

    @staticmethod
    def find(points: List['Point3D']) -> Tuple['Point3D', float]:
        from compgeom.kernel import Point3D, distance_3d
        if len(points) < 4:
            if len(points) == 2:
                p1, p2 = points
                center = Point3D((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0, getattr(p1, 'z', 0.0) + getattr(p2, 'z', 0.0) / 2.0)
                return center, distance_3d(p1, p2) / 2.0
            return Point3D(0, 0, 0), 0.0

        try:
            from scipy.spatial import Delaunay, ConvexHull
            import numpy as np
        except ImportError:
            raise ImportError("LargestEmptySphere requires 'scipy' and 'numpy'.")

        pts_array = np.array([[p.x, p.y, getattr(p, 'z', 0.0)] for p in points])
        delaunay = Delaunay(pts_array)
        
        from compgeom.kernel.sphere import from_four_points
        
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
            center = Point3D((p1.x+p2.x+p3.x)/3.0, (p1.y+p2.y+p3.y)/3.0, (getattr(p1,'z',0)+getattr(p2,'z',0)+getattr(p3,'z',0))/3.0)
            
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
                j = (i+1)%3
                u, v = simplex[i], simplex[j]
                edges.add((min(u,v), max(u,v)))
                
        for u, v in edges:
            p1, p2 = points[u], points[v]
            mid = Point3D((p1.x+p2.x)/2.0, (p1.y+p2.y)/2.0, (getattr(p1,'z',0)+getattr(p2,'z',0))/2.0)
            min_d = min(distance_3d(mid, p) for p in points)
            if min_d > max_radius:
                max_radius = min_d
                best_center = mid

        if best_center is None:
             return Point3D(0,0,0), 0.0
             
        return best_center, max_radius


class LargestEmptyOrientedBox:
    """Approximates the largest empty oriented box within a 3D convex hull."""

    @staticmethod
    def find(points: List['Point3D']) -> dict:
        import numpy as np
        from scipy.spatial import ConvexHull, Delaunay
        from compgeom.kernel import Point3D

        if len(points) < 4:
            return {"volume": 0.0, "center": Point3D(0,0,0), "width": 0.0, "height": 0.0, "depth": 0.0, "axes": ((1,0,0),(0,1,0),(0,0,1)), "corners": []}

        pts_array = np.array([[p.x, p.y, getattr(p, 'z', 0.0)] for p in points])
        try:
            hull = ConvexHull(pts_array)
            delaunay = Delaunay(pts_array)
        except Exception:
            return {"volume": 0.0, "center": Point3D(0,0,0), "width": 0.0, "height": 0.0, "depth": 0.0, "axes": ((1,0,0),(0,1,0),(0,0,1)), "corners": []}

        seeds = []
        
        # 1. Largest Empty Sphere center
        try:
            from compgeom.algo.proximity import LargestEmptySphere
            les_center, _ = LargestEmptySphere.find(points)
            seeds.append(np.array([les_center.x, les_center.y, les_center.z]))
        except ImportError:
            pass
            
        # 2. Top Delaunay tetrahedra
        vols = []
        centroids = []
        for simplex in delaunay.simplices:
            pts = pts_array[simplex]
            vol = abs(np.linalg.det(np.vstack((pts.T, np.ones(4))))) / 6.0
            vols.append(vol)
            centroids.append(np.mean(pts, axis=0))
            
        top_indices = np.argsort(vols)[-10:]
        for idx in top_indices:
            c = centroids[idx]
            if delaunay.find_simplex(c) >= 0:
                seeds.append(c)

        orientations = []
        orientations.append(np.eye(3))
        
        centroid = np.mean(pts_array, axis=0)
        cov = np.cov((pts_array - centroid).T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        idx = eigenvalues.argsort()[::-1]
        pca_axes = eigenvectors[:, idx].T
        orientations.append(pca_axes)
        
        face_areas = []
        for simplex in hull.simplices:
            p1, p2, p3 = pts_array[simplex]
            area = np.linalg.norm(np.cross(p2-p1, p3-p1)) * 0.5
            face_areas.append(area)
        
        top_faces = np.argsort(face_areas)[-3:]
        for idx in top_faces:
            p1, p2, p3 = pts_array[hull.simplices[idx]]
            n = np.array(np.cross(p2-p1, p3-p1), dtype=float)
            norm_n = np.linalg.norm(n)
            if norm_n > 1e-9:
                n = n / norm_n
                t1 = p2 - p1
                norm_t1 = np.linalg.norm(t1)
                if norm_t1 > 1e-9:
                    t1 = t1 / norm_t1
                    t2 = np.cross(n, t1)
                    orientations.append(np.vstack((t1, t2, n)))

        def expand_box(points_loc, hull_eq_loc, order, initial_R):
            bounds = [-initial_R, initial_R, -initial_R, initial_R, -initial_R, initial_R]
            eps = 1e-7
            for d in order:
                if d == "+x":
                    p_lim = float('inf')
                    for p in points_loc:
                        if p[0] > bounds[1] + eps and bounds[2]-eps <= p[1] <= bounds[3]+eps and bounds[4]-eps <= p[2] <= bounds[5]+eps:
                            if p[0] < p_lim: p_lim = p[0]
                    h_lim = float('inf')
                    for eq in hull_eq_loc:
                        A, B, C, D = eq
                        if A > eps:
                            for y in [bounds[2], bounds[3]]:
                                for z in [bounds[4], bounds[5]]:
                                    val = (-D - B*y - C*z) / A
                                    if val < h_lim: h_lim = val
                    bounds[1] = min(p_lim, h_lim) - eps

                elif d == "-x":
                    p_lim = -float('inf')
                    for p in points_loc:
                        if p[0] < bounds[0] - eps and bounds[2]-eps <= p[1] <= bounds[3]+eps and bounds[4]-eps <= p[2] <= bounds[5]+eps:
                            if p[0] > p_lim: p_lim = p[0]
                    h_lim = -float('inf')
                    for eq in hull_eq_loc:
                        A, B, C, D = eq
                        if A < -eps:
                            for y in [bounds[2], bounds[3]]:
                                for z in [bounds[4], bounds[5]]:
                                    val = (-D - B*y - C*z) / A
                                    if val > h_lim: h_lim = val
                    bounds[0] = max(p_lim, h_lim) + eps

                elif d == "+y":
                    p_lim = float('inf')
                    for p in points_loc:
                        if p[1] > bounds[3] + eps and bounds[0]-eps <= p[0] <= bounds[1]+eps and bounds[4]-eps <= p[2] <= bounds[5]+eps:
                            if p[1] < p_lim: p_lim = p[1]
                    h_lim = float('inf')
                    for eq in hull_eq_loc:
                        A, B, C, D = eq
                        if B > eps:
                            for x in [bounds[0], bounds[1]]:
                                for z in [bounds[4], bounds[5]]:
                                    val = (-D - A*x - C*z) / B
                                    if val < h_lim: h_lim = val
                    bounds[3] = min(p_lim, h_lim) - eps

                elif d == "-y":
                    p_lim = -float('inf')
                    for p in points_loc:
                        if p[1] < bounds[2] - eps and bounds[0]-eps <= p[0] <= bounds[1]+eps and bounds[4]-eps <= p[2] <= bounds[5]+eps:
                            if p[1] > p_lim: p_lim = p[1]
                    h_lim = -float('inf')
                    for eq in hull_eq_loc:
                        A, B, C, D = eq
                        if B < -eps:
                            for x in [bounds[0], bounds[1]]:
                                for z in [bounds[4], bounds[5]]:
                                    val = (-D - A*x - C*z) / B
                                    if val > h_lim: h_lim = val
                    bounds[2] = max(p_lim, h_lim) + eps

                elif d == "+z":
                    p_lim = float('inf')
                    for p in points_loc:
                        if p[2] > bounds[5] + eps and bounds[0]-eps <= p[0] <= bounds[1]+eps and bounds[2]-eps <= p[1] <= bounds[3]+eps:
                            if p[2] < p_lim: p_lim = p[2]
                    h_lim = float('inf')
                    for eq in hull_eq_loc:
                        A, B, C, D = eq
                        if C > eps:
                            for x in [bounds[0], bounds[1]]:
                                for y in [bounds[2], bounds[3]]:
                                    val = (-D - A*x - B*y) / C
                                    if val < h_lim: h_lim = val
                    bounds[5] = min(p_lim, h_lim) - eps

                elif d == "-z":
                    p_lim = -float('inf')
                    for p in points_loc:
                        if p[2] < bounds[4] - eps and bounds[0]-eps <= p[0] <= bounds[1]+eps and bounds[2]-eps <= p[1] <= bounds[3]+eps:
                            if p[2] > p_lim: p_lim = p[2]
                    h_lim = -float('inf')
                    for eq in hull_eq_loc:
                        A, B, C, D = eq
                        if C < -eps:
                            for x in [bounds[0], bounds[1]]:
                                for y in [bounds[2], bounds[3]]:
                                    val = (-D - A*x - B*y) / C
                                    if val > h_lim: h_lim = val
                    bounds[4] = max(p_lim, h_lim) + eps

            bounds = [min(0, bounds[0]), max(0, bounds[1]), min(0, bounds[2]), max(0, bounds[3]), min(0, bounds[4]), max(0, bounds[5])]
            vol = (bounds[1] - bounds[0]) * (bounds[3] - bounds[2]) * (bounds[5] - bounds[4])
            return bounds, vol

        best_vol = -1.0
        best_box = None

        orders = [
            ["+x", "-x", "+y", "-y", "+z", "-z"],
            ["+y", "-y", "+z", "-z", "+x", "-x"],
            ["+z", "-z", "+x", "-x", "+y", "-y"],
            ["-x", "+x", "-y", "+y", "-z", "+z"],
            ["-y", "+y", "-z", "+z", "-x", "+x"],
            ["-z", "+z", "-x", "+x", "-y", "+y"]
        ]

        for C in seeds:
            r_nearest = float('inf')
            for p in pts_array:
                d = np.linalg.norm(p - C)
                if d > 1e-9 and d < r_nearest: r_nearest = d
            for eq in hull.equations:
                d = -(np.dot(eq[:3], C) + eq[3]) / np.linalg.norm(eq[:3])
                if d > 1e-9 and d < r_nearest: r_nearest = d
            
            if r_nearest == float('inf'): r_nearest = 0.0
            initial_R = (r_nearest / np.sqrt(3.0)) * 0.98

            for U in orientations:
                P_loc = (pts_array - C) @ U.T
                
                hull_eq_loc = []
                for eq in hull.equations:
                    Ng = eq[:3]
                    Dg = eq[3]
                    Al = np.dot(Ng, U[0])
                    Bl = np.dot(Ng, U[1])
                    Cl = np.dot(Ng, U[2])
                    Dl = np.dot(Ng, C) + Dg
                    hull_eq_loc.append([Al, Bl, Cl, Dl])
                
                for order in orders:
                    bounds, vol = expand_box(P_loc, hull_eq_loc, order, initial_R)
                    if vol > best_vol:
                        best_vol = vol
                        best_box = (C, U, bounds)

        if not best_box:
             return {"volume": 0.0, "center": Point3D(0,0,0), "width": 0.0, "height": 0.0, "depth": 0.0, "axes": ((1,0,0),(0,1,0),(0,0,1)), "corners": []}

        C, U, bounds = best_box
        cx_loc = (bounds[0] + bounds[1]) / 2.0
        cy_loc = (bounds[2] + bounds[3]) / 2.0
        cz_loc = (bounds[4] + bounds[5]) / 2.0
        
        w = bounds[1] - bounds[0]
        h = bounds[3] - bounds[2]
        d = bounds[5] - bounds[4]
        
        center_global = C + cx_loc * U[0] + cy_loc * U[1] + cz_loc * U[2]
        center = Point3D(center_global[0], center_global[1], center_global[2])
        
        corners = []
        for dx in [-w/2, w/2]:
            for dy in [-h/2, h/2]:
                for dz in [-d/2, d/2]:
                    cg = center_global + dx*U[0] + dy*U[1] + dz*U[2]
                    corners.append(Point3D(cg[0], cg[1], cg[2]))
                    
        return {
            "center": center,
            "width": w,
            "height": h,
            "depth": d,
            "volume": best_vol,
            "axes": (tuple(float(x) for x in U[0]), tuple(float(x) for x in U[1]), tuple(float(x) for x in U[2])),
            "corners": corners
        }


class LargestEmptyOrientedEllipsoid:
    """Finds a large volume oriented ellipsoid that is empty of points and inside the 3D convex hull."""

    @staticmethod
    def find(points: List['Point3D']) -> dict:
        import numpy as np
        from scipy.spatial import ConvexHull, Delaunay
        from compgeom.kernel import Point3D

        if len(points) < 4:
            return {"volume": 0.0, "center": Point3D(0,0,0), "radii": (0,0,0), "axes": ((1,0,0),(0,1,0),(0,0,1))}

        pts_array = np.array([[p.x, p.y, getattr(p, 'z', 0.0)] for p in points])
        try:
            hull = ConvexHull(pts_array)
            delaunay = Delaunay(pts_array)
        except Exception:
            return {"volume": 0.0, "center": Point3D(0,0,0), "radii": (0,0,0), "axes": ((1,0,0),(0,1,0),(0,0,1))}

        seeds = []
        try:
            from compgeom.algo.proximity import LargestEmptySphere
            les_center, les_r = LargestEmptySphere.find(points)
            seeds.append((np.array([les_center.x, les_center.y, les_center.z]), les_r))
        except Exception:
            pass
            
        # Add top Delaunay centroids as seeds
        for simplex in delaunay.simplices:
            pts = pts_array[simplex]
            c = np.mean(pts, axis=0)
            if delaunay.find_simplex(c) >= 0:
                # Find min dist to points/hull for initial R
                min_d = np.min(np.linalg.norm(pts_array - c, axis=1))
                for eq in hull.equations:
                    d_hull = abs(np.dot(eq[:3], c) + eq[3]) / np.linalg.norm(eq[:3])
                    if d_hull < min_d: min_d = d_hull
                seeds.append((c, min_d))
        
        seeds = sorted(seeds, key=lambda x: x[1], reverse=True)[:5]

        orientations = [np.eye(3)]
        centroid = np.mean(pts_array, axis=0)
        cov = np.cov((pts_array - centroid).T)
        _, eigenvectors = np.linalg.eigh(cov)
        orientations.append(eigenvectors.T) # PCA axes
        
        for simplex in hull.simplices[:3]: # Add a few face-aligned axes
            p1, p2, p3 = pts_array[simplex]
            n = np.array(np.cross(p2-p1, p3-p1), dtype=float)
            n_norm = np.linalg.norm(n)
            if n_norm > 1e-9:
                n /= n_norm
                t1 = (p2-p1) / np.linalg.norm(p2-p1)
                t2 = np.cross(n, t1)
                orientations.append(np.vstack((t1, t2, n)))

        def optimize_ellipsoid(C, U, initial_r):
            # Coordinate descent for a, b, c
            # local coords: P_loc = (P - C) @ U.T
            P_loc = (pts_array - C) @ U.T
            # Plane eqs in local coords: A*x + B*y + C*z + D = 0
            hull_eq_loc = []
            for eq in hull.equations:
                Ng, Dg = eq[:3], eq[3]
                Al, Bl, Cl = np.dot(Ng, U[0]), np.dot(Ng, U[1]), np.dot(Ng, U[2])
                Dl = np.dot(Ng, C) + Dg
                hull_eq_loc.append([Al, Bl, Cl, Dl])

            # Start with a small sphere
            abc = np.array([initial_r, initial_r, initial_r], dtype=float) * 0.95
            
            for _ in range(10): # Iterations of coordinate descent
                for i in range(3):
                    # Maximize abc[i]
                    other_idx = [j for j in range(3) if j != i]
                    
                    max_val_sq = float('inf')
                    
                    # Point constraints: (x/a)^2 + (y/b)^2 + (z/c)^2 >= 1
                    # (val/abc[i])^2 >= 1 - sum((other_val/abc[other])^2)
                    for p in P_loc:
                        sum_others = (p[other_idx[0]]/abc[other_idx[0]])**2 + (p[other_idx[1]]/abc[other_idx[1]])**2
                        if sum_others < 1.0:
                            limit_sq = (p[i]**2) / (1.0 - sum_others)
                            if limit_sq < max_val_sq: max_val_sq = limit_sq
                    
                    # Plane constraints: sum((Coeff[j] * abc[j])^2) <= D^2
                    for eq in hull_eq_loc:
                        Ai = eq[i]
                        SumOthers = (eq[other_idx[0]]*abc[other_idx[0]])**2 + (eq[other_idx[1]]*abc[other_idx[1]])**2
                        D_sq = eq[3]**2
                        if Ai**2 > 1e-12:
                            if D_sq > SumOthers:
                                limit_sq = (D_sq - SumOthers) / (Ai**2)
                                if limit_sq < max_val_sq: max_val_sq = limit_sq
                            else:
                                max_val_sq = 0.0 # Already intersecting
                    
                    if max_val_sq <= 0: abc[i] = 1e-6
                    else: abc[i] = np.sqrt(max_val_sq) * 0.999 # Small buffer
            
            vol = (4/3) * np.pi * abc[0] * abc[1] * abc[2]
            return abc, vol

        best_vol = -1.0
        best_res = None

        for C, r in seeds:
            for U in orientations:
                abc, vol = optimize_ellipsoid(C, U, r)
                if vol > best_vol:
                    best_vol = vol
                    best_res = (C, U, abc)

        if not best_res:
            return {"volume": 0.0, "center": Point3D(0,0,0), "radii": (0,0,0), "axes": ((1,0,0),(0,1,0),(0,0,1))}

        C, U, abc = best_res
        return {
            "center": Point3D(C[0], C[1], C[2]),
            "radii": tuple(float(x) for x in abc),
            "axes": (tuple(float(x) for x in U[0]), tuple(float(x) for x in U[1]), tuple(float(x) for x in U[2])),
            "volume": best_vol
        }

class LargestEmptyOrientedRectangle:
    """Finds a large volume oriented rectangle that is empty of points and inside the 2D convex hull."""

    @staticmethod
    def find(points: List['Point2D']) -> dict:
        import numpy as np
        from scipy.spatial import ConvexHull, Delaunay
        from compgeom.kernel import Point2D, distance

        if len(points) < 3:
            return {"area": 0.0, "center": Point2D(0,0), "width": 0.0, "height": 0.0, "angle": 0.0, "corners": []}

        pts_array = np.array([[p.x, p.y] for p in points])
        try:
            hull = ConvexHull(pts_array)
            delaunay = Delaunay(pts_array)
        except Exception:
            return {"area": 0.0, "center": Point2D(0,0), "width": 0.0, "height": 0.0, "angle": 0.0, "corners": []}

        seeds = []
        try:
            from compgeom.algo.proximity import LargestEmptyCircle
            lec_center, lec_r = LargestEmptyCircle.find(points)
            seeds.append((np.array([lec_center.x, lec_center.y]), lec_r))
        except Exception:
            pass
            
        for simplex in delaunay.simplices:
            pts = pts_array[simplex]
            c = np.mean(pts, axis=0)
            if delaunay.find_simplex(c) >= 0:
                min_d = np.min(np.linalg.norm(pts_array - c, axis=1))
                for eq in hull.equations:
                    d_hull = abs(np.dot(eq[:2], c) + eq[2]) / np.linalg.norm(eq[:2])
                    if d_hull < min_d: min_d = d_hull
                seeds.append((c, min_d))
        
        seeds = sorted(seeds, key=lambda x: x[1], reverse=True)[:10]

        orientations = [np.eye(2)]
        centroid = np.mean(pts_array, axis=0)
        cov = np.cov((pts_array - centroid).T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        idx = eigenvalues.argsort()[::-1]
        orientations.append(eigenvectors[:, idx].T)
        
        for simplex in hull.simplices:
            p1, p2 = pts_array[simplex]
            v = p2 - p1
            v_norm = np.linalg.norm(v)
            if v_norm > 1e-9:
                t1 = v / v_norm
                t2 = np.array([-t1[1], t1[0]])
                orientations.append(np.vstack((t1, t2)))

        def expand_rect(C, U, initial_r):
            P_loc = (pts_array - C) @ U.T
            hull_eq_loc = []
            for eq in hull.equations:
                Ng, Dg = eq[:2], eq[2]
                Al, Bl = np.dot(Ng, U[0]), np.dot(Ng, U[1])
                Dl = np.dot(Ng, C) + Dg
                hull_eq_loc.append([Al, Bl, Dl])

            side = (initial_r / np.sqrt(2.0)) * 0.95
            bounds = [-side, side, -side, side]
            
            orders = [["+x","-x","+y","-y"], ["+y","-y","+x","-x"], ["-x","+x","-y","+y"], ["-y","+y","-x","+x"]]
            best_local_area = -1.0
            best_local_bounds = bounds
            
            eps = 1e-7
            for order in orders:
                cur_bounds = list(bounds)
                for d in order:
                    if d == "+x":
                        p_lim = float('inf')
                        for p in P_loc:
                            if p[0] > cur_bounds[1] + eps and cur_bounds[2]-eps <= p[1] <= cur_bounds[3]+eps:
                                if p[0] < p_lim: p_lim = p[0]
                        h_lim = float('inf')
                        for eq in hull_eq_loc:
                            if eq[0] > eps:
                                for y in [cur_bounds[2], cur_bounds[3]]:
                                    val = (-eq[2] - eq[1]*y) / eq[0]
                                    if val < h_lim: h_lim = val
                        cur_bounds[1] = min(p_lim, h_lim) - eps
                    elif d == "-x":
                        p_lim = -float('inf')
                        for p in P_loc:
                            if p[0] < cur_bounds[0] - eps and cur_bounds[2]-eps <= p[1] <= cur_bounds[3]+eps:
                                if p[0] > p_lim: p_lim = p[0]
                        h_lim = -float('inf')
                        for eq in hull_eq_loc:
                            if eq[0] < -eps:
                                for y in [cur_bounds[2], cur_bounds[3]]:
                                    val = (-eq[2] - eq[1]*y) / eq[0]
                                    if val > h_lim: h_lim = val
                        cur_bounds[0] = max(p_lim, h_lim) + eps
                    elif d == "+y":
                        p_lim = float('inf')
                        for p in P_loc:
                            if p[1] > cur_bounds[3] + eps and cur_bounds[0]-eps <= p[0] <= cur_bounds[1]+eps:
                                if p[1] < p_lim: p_lim = p[1]
                        h_lim = float('inf')
                        for eq in hull_eq_loc:
                            if eq[1] > eps:
                                for x in [cur_bounds[0], cur_bounds[1]]:
                                    val = (-eq[2] - eq[0]*x) / eq[1]
                                    if val < h_lim: h_lim = val
                        cur_bounds[3] = min(p_lim, h_lim) - eps
                    elif d == "-y":
                        p_lim = -float('inf')
                        for p in P_loc:
                            if p[1] < cur_bounds[2] - eps and cur_bounds[0]-eps <= p[0] <= cur_bounds[1]+eps:
                                if p[1] > p_lim: p_lim = p[1]
                        h_lim = -float('inf')
                        for eq in hull_eq_loc:
                            if eq[1] < -eps:
                                for x in [cur_bounds[0], cur_bounds[1]]:
                                    val = (-eq[2] - eq[0]*x) / eq[1]
                                    if val > h_lim: h_lim = val
                        cur_bounds[2] = max(p_lim, h_lim) + eps
                
                area = (cur_bounds[1]-cur_bounds[0]) * (cur_bounds[3]-cur_bounds[2])
                if area > best_local_area:
                    best_local_area = area
                    best_local_bounds = cur_bounds
            return best_local_bounds, best_local_area

        best_area = -1.0
        best_res = None

        for C, r in seeds:
            for U in orientations:
                bounds, area = expand_rect(C, U, r)
                if area > best_area:
                    best_area = area
                    best_res = (C, U, bounds)

        if not best_res:
            return {"area": 0.0, "center": Point2D(0,0), "width": 0.0, "height": 0.0, "angle": 0.0, "corners": []}

        C, U, bounds = best_res
        cx_loc, cy_loc = (bounds[0]+bounds[1])/2.0, (bounds[2]+bounds[3])/2.0
        c_global = C + cx_loc * U[0] + cy_loc * U[1]
        w, h = bounds[1]-bounds[0], bounds[3]-bounds[2]
        angle = np.arctan2(U[0][1], U[0][0])
        corners = [Point2D(p[0], p[1]) for p in [c_global + dx*U[0] + dy*U[1] for dx, dy in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]]
        return {"center": Point2D(c_global[0], c_global[1]), "width": w, "height": h, "area": best_area, "angle": float(angle), "corners": corners}

class LargestEmptyOrientedEllipse:
    """Finds a large volume oriented ellipse that is empty of points and inside the 2D convex hull."""

    @staticmethod
    def find(points: List['Point2D']) -> dict:
        import numpy as np
        from scipy.spatial import ConvexHull, Delaunay
        from compgeom.kernel import Point2D

        if len(points) < 3:
            return {"area": 0.0, "center": Point2D(0,0), "radii": (0,0), "angle": 0.0}

        pts_array = np.array([[p.x, p.y] for p in points])
        try:
            hull = ConvexHull(pts_array)
            delaunay = Delaunay(pts_array)
        except Exception:
            return {"area": 0.0, "center": Point2D(0,0), "radii": (0,0), "angle": 0.0}

        seeds = []
        try:
            from compgeom.algo.proximity import LargestEmptyCircle
            lec_center, lec_r = LargestEmptyCircle.find(points)
            seeds.append((np.array([lec_center.x, lec_center.y]), lec_r))
        except Exception:
            pass
            
        for simplex in delaunay.simplices:
            pts = pts_array[simplex]
            c = np.mean(pts, axis=0)
            if delaunay.find_simplex(c) >= 0:
                min_d = np.min(np.linalg.norm(pts_array - c, axis=1))
                for eq in hull.equations:
                    d_hull = abs(np.dot(eq[:2], c) + eq[2]) / np.linalg.norm(eq[:2])
                    if d_hull < min_d: min_d = d_hull
                seeds.append((c, min_d))
        
        seeds = sorted(seeds, key=lambda x: x[1], reverse=True)[:5]

        orientations = [np.eye(2)]
        centroid = np.mean(pts_array, axis=0)
        cov = np.cov((pts_array - centroid).T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        idx = eigenvalues.argsort()[::-1]
        orientations.append(eigenvectors[:, idx].T)
        
        for simplex in hull.simplices[:5]:
            p1, p2 = pts_array[simplex]
            v = p2 - p1
            v_norm = np.linalg.norm(v)
            if v_norm > 1e-9:
                t1 = v / v_norm
                t2 = np.array([-t1[1], t1[0]])
                orientations.append(np.vstack((t1, t2)))

        def optimize_ellipse(C, U, initial_r):
            P_loc = (pts_array - C) @ U.T
            hull_eq_loc = []
            for eq in hull.equations:
                Ng, Dg = eq[:2], eq[2]
                Al, Bl = np.dot(Ng, U[0]), np.dot(Ng, U[1])
                Dl = np.dot(Ng, C) + Dg
                hull_eq_loc.append([Al, Bl, Dl])

            ab = np.array([initial_r, initial_r], dtype=float) * 0.95
            
            for _ in range(10):
                for i in range(2):
                    other_idx = 1 - i
                    max_val_sq = float('inf')
                    
                    for p in P_loc:
                        other_term = (p[other_idx]/ab[other_idx])**2
                        if other_term < 1.0:
                            limit_sq = (p[i]**2) / (1.0 - other_term)
                            if limit_sq < max_val_sq: max_val_sq = limit_sq
                    
                    for eq in hull_eq_loc:
                        Ai = eq[i]
                        OtherTerm = (eq[other_idx]*ab[other_idx])**2
                        D_sq = eq[2]**2
                        if Ai**2 > 1e-12:
                            if D_sq > OtherTerm:
                                limit_sq = (D_sq - OtherTerm) / (Ai**2)
                                if limit_sq < max_val_sq: max_val_sq = limit_sq
                            else:
                                max_val_sq = 0.0
                    
                    if max_val_sq <= 0: ab[i] = 1e-6
                    else: ab[i] = np.sqrt(max_val_sq) * 0.999
            
            area = np.pi * ab[0] * ab[1]
            return ab, area

        best_area = -1.0
        best_res = None

        for C, r in seeds:
            for U in orientations:
                ab, area = optimize_ellipse(C, U, r)
                if area > best_area:
                    best_area = area
                    best_res = (C, U, ab)

        if not best_res:
            return {"area": 0.0, "center": Point2D(0,0), "radii": (0,0), "angle": 0.0}

        C, U, ab = best_res
        angle = np.arctan2(U[0][1], U[0][0])
        return {
            "center": Point2D(C[0], C[1]),
            "radii": (float(ab[0]), float(ab[1])),
            "angle": float(angle),
            "area": best_area,
            "axes": (tuple(float(x) for x in U[0]), tuple(float(x) for x in U[1]))
        }
