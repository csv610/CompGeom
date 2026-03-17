"""Visibility algorithms for polygons."""

from __future__ import annotations

from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .polygon import Polygon

from ..kernel import Point2D
from .line_segment import ray_segment_intersection
from .tolerance import are_close


def compute_visibility_polygon(viewpoint: Point2D, polygon: Polygon | list[Point2D]) -> Polygon:
    """
    Computes the visibility polygon from a given viewpoint within or on the boundary of a polygon.
    Uses a simple ray-casting approach (for demonstration, not optimal).
    """
    from .polygon import Polygon
    
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    if not poly_obj.contains_point(viewpoint) and not poly_obj.point_on_boundary(viewpoint):
        raise ValueError("Viewpoint must be inside or on the boundary of the polygon.")

    vertices = list(poly_obj.vertices)
    
    rays: list[float] = []
    
    for v in poly_obj.vertices:
        angle = math.atan2(v.y - viewpoint.y, v.x - viewpoint.x)
        rays.extend([angle - 1e-9, angle, angle + 1e-9])

    visibility_vertices = []
    for angle in sorted(rays):
        closest_dist = float('inf')
        closest_point = None
        
        for i in range(len(vertices)):
            p1, p2 = vertices[i], vertices[(i + 1) % len(vertices)]
            res = ray_segment_intersection(viewpoint, angle, p1, p2)
            if res:
                ray_t, hit = res
                d = (hit.x - viewpoint.x)**2 + (hit.y - viewpoint.y)**2
                if d < closest_dist:
                    closest_dist = d
                    closest_point = hit
        
        if closest_point:
            if not visibility_vertices or not are_close(visibility_vertices[-1], closest_point):
                visibility_vertices.append(closest_point)

    return Polygon(visibility_vertices).cleanup()


__all__ = ["compute_visibility_polygon"]
