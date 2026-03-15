"""Shared polygon helper functions."""

from __future__ import annotations

from typing import Callable, Sequence

from ..kernel import Point2D, is_on_segment
from .line_segment import proper_segment_intersection
from .polygon import Polygon
from .tolerance import are_close, EPSILON


def ensure_ccw(polygon: Polygon | Sequence[Point2D]) -> Polygon:
    if isinstance(polygon, Polygon):
        return polygon.ensure_ccw()
    return Polygon(polygon).ensure_ccw()


def ensure_cw(polygon: Polygon | Sequence[Point2D]) -> Polygon:
    if isinstance(polygon, Polygon):
        return polygon.ensure_cw()
    return Polygon(polygon).ensure_cw()


def rotate_polygon(polygon: Polygon | Sequence[Point2D], angle: float, center: Point2D | None = None) -> Polygon:
    if isinstance(polygon, Polygon):
        return polygon.rotate(angle, center)
    return Polygon(polygon).rotate(angle, center)


def same_point(a: Point2D, b: Point2D, tolerance: float = EPSILON) -> bool:
    return are_close(a, b, tolerance)


def point_on_boundary(point: Point2D, polygon: Polygon | Sequence[Point2D]) -> bool:
    if isinstance(polygon, Polygon):
        return polygon.point_on_boundary(point)
    return Polygon(polygon).point_on_boundary(point)


def cleanup_polygon(polygon: Polygon | Sequence[Point2D]) -> Polygon:
    if isinstance(polygon, Polygon):
        return polygon.cleanup()
    return Polygon(polygon).cleanup()


def segment_inside_boundaries(
    start: Point2D,
    end: Point2D,
    boundaries: list[Polygon | list[Point2D]],
    midpoint_inside: Callable[[Point2D], bool],
    allow_boundary_endpoint: Point2D | None = None,
) -> bool:
    midpoint = Point2D((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not midpoint_inside(midpoint):
        return False

    for boundary in boundaries:
        pts = boundary.vertices if isinstance(boundary, Polygon) else boundary
        for index, edge_start in enumerate(pts):
            edge_end = pts[(index + 1) % len(pts)]
            shared_endpoint = (
                are_close(start, edge_start) or
                are_close(start, edge_end) or
                are_close(end, edge_start) or
                are_close(end, edge_end)
            )
            if shared_endpoint:
                continue
            if allow_boundary_endpoint is not None and (
                are_close(edge_start, allow_boundary_endpoint) or
                are_close(edge_end, allow_boundary_endpoint)
            ):
                continue
            if proper_segment_intersection(start, end, edge_start, edge_end):
                return False
            return True

__all__ = [
    "ensure_ccw",
    "ensure_cw",
    "rotate_polygon",
    "same_point",
    "point_on_boundary",
    "cleanup_polygon",
    "segment_inside_boundaries",
]
