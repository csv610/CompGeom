"""Distance, intersection, and enclosing-shape algorithms."""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, List, Optional, Tuple, Union

from ..kernel import (
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
from ..polygon.convex_hull import GrahamScan
from ..polygon.polygon import is_point_in_polygon


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
        from ..mesh.delaunay_triangulation import triangulate
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
    "closest_pair",
    "do_intersect",
    "farthest_pair",
    "get_circle_three_points",
    "get_circle_two_points",
    "minkowski_sum",
    "support",
    "welzl",
]
