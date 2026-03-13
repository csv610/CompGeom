"""Visibility and kernel algorithms for polygons."""

from __future__ import annotations

import math

from ..kernel import EPSILON, Point2D, clip_polygon
from .line_segment import ray_segment_intersection
from .polygon import Polygon
from .polygon_utils import cleanup_polygon


def visibility_polygon(viewpoint: Point2D, polygon: list[Point2D]) -> list[Point2D]:
    polygon_shape = Polygon(polygon)
    if not polygon_shape.contains_point(viewpoint):
        raise ValueError("Viewpoint must lie inside or on the boundary of the polygon.")

    intersections: list[tuple[float, float, Point2D]] = []
    perturbation = 1e-7
    for vertex in polygon:
        base_angle = math.atan2(vertex.y - viewpoint.y, vertex.x - viewpoint.x)
        for angle in (base_angle - perturbation, base_angle, base_angle + perturbation):
            best: tuple[float, Point2D] | None = None
            for index, start in enumerate(polygon):
                end = polygon[(index + 1) % len(polygon)]
                hit = ray_segment_intersection(viewpoint, angle, start, end)
                if hit is None:
                    continue
                hit_distance, point = hit
                if hit_distance < -EPSILON:
                    continue
                if best is None or hit_distance < best[0]:
                    best = (hit_distance, point)
            if best is not None:
                intersections.append((angle, best[0], best[1]))

    intersections.sort(key=lambda item: (item[0], item[1]))
    return cleanup_polygon([point for _, _, point in intersections])


def polygon_kernel(polygon: list[Point2D]) -> list[Point2D]:
    polygon_shape = Polygon(polygon).ensure_ccw()
    ordered = polygon_shape.as_list()
    if len(ordered) < 3:
        return []

    kernel = list(ordered)
    for index, start in enumerate(ordered):
        end = ordered[(index + 1) % len(ordered)]
        kernel = clip_polygon(kernel, start, end)
        if not kernel:
            return []
    return cleanup_polygon(kernel)


__all__ = ["polygon_kernel", "visibility_polygon"]
