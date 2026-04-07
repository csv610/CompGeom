from __future__ import annotations

import math
from typing import List, Tuple

from compgeom.kernel import (
    Point2D,
    distance,
    ray_segment_intersection,
    triangle_circumcenter,
)
from compgeom.mesh.surface.trimesh.delaunay_triangulation import triangulate
from compgeom.polygon.convex_hull import GrahamScan
from compgeom.polygon.polygon_metrics import is_point_in_polygon

__all__ = ["find_largest_empty_circle", "visualize_largest_empty_circle"]


def find_largest_empty_circle(points: List[Point2D]) -> Tuple[Point2D, float]:
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


def visualize_largest_empty_circle(points: List[Point2D], center: Point2D, radius: float) -> str:
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

    svg.append(
        f'<circle cx="{tx(center.x)}" cy="{ty(center.y)}" r="{radius * (width - 2 * padding) / (max_x - min_x) if max_x > min_x else 0}" fill="blue" fill-opacity="0.2" stroke="blue" stroke-width="2" />'
    )
    svg.append(f'<circle cx="{tx(center.x)}" cy="{ty(center.y)}" r="4" fill="red" />')

    svg.append("</svg>")
    return "\n".join(svg)
