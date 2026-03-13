"""Shared polygon helper functions."""

from __future__ import annotations

from typing import Callable

from ..kernel import Point2D, cross_product, is_on_segment
from ..kernel import signed_area_twice
from .line_segment import proper_segment_intersection


def ensure_ccw(polygon: list[Point2D]) -> list[Point2D]:
    return polygon if signed_area_twice(polygon) >= 0 else list(reversed(polygon))


def ensure_cw(polygon: list[Point2D]) -> list[Point2D]:
    return polygon if signed_area_twice(polygon) <= 0 else list(reversed(polygon))


def same_point(a: Point2D, b: Point2D, tolerance: float = 1e-7) -> bool:
    return abs(a.x - b.x) <= tolerance and abs(a.y - b.y) <= tolerance


def point_on_boundary(point: Point2D, polygon: list[Point2D]) -> bool:
    n = len(polygon)
    if n == 0:
        return False
    for i in range(n):
        if is_on_segment(point, polygon[i], polygon[(i + 1) % n]):
            return True
    return False


def cleanup_polygon(points: list[Point2D]) -> list[Point2D]:
    if not points:
        return []

    cleaned: list[Point2D] = []
    for point in points:
        if cleaned and same_point(point, cleaned[-1]):
            continue
        cleaned.append(point)

    if len(cleaned) > 1 and same_point(cleaned[0], cleaned[-1]):
        cleaned.pop()

    simplified: list[Point2D] = []
    for point in cleaned:
        if len(simplified) < 2:
            simplified.append(point)
            continue
        if abs(cross_product(simplified[-2], simplified[-1], point)) <= 1e-7 and is_on_segment(
            simplified[-1], simplified[-2], point
        ):
            simplified[-1] = point
            continue
        simplified.append(point)

    if len(simplified) >= 3 and abs(cross_product(simplified[-2], simplified[-1], simplified[0])) <= 1e-7:
        if is_on_segment(simplified[-1], simplified[-2], simplified[0]):
            simplified.pop()
    return simplified


def segment_inside_boundaries(
    start: Point2D,
    end: Point2D,
    boundaries: list[list[Point2D]],
    midpoint_inside: Callable[[Point2D], bool],
    allow_boundary_endpoint: Point2D | None = None,
) -> bool:
    midpoint = Point2D((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not midpoint_inside(midpoint):
        return False

    for boundary in boundaries:
        for index, edge_start in enumerate(boundary):
            edge_end = boundary[(index + 1) % len(boundary)]
            shared_endpoint = start == edge_start or start == edge_end or end == edge_start or end == edge_end
            if shared_endpoint:
                continue
            if allow_boundary_endpoint is not None and (
                edge_start == allow_boundary_endpoint or edge_end == allow_boundary_endpoint
            ):
                continue
            if proper_segment_intersection(start, end, edge_start, edge_end):
                return False
    return True


__all__ = [
    "cleanup_polygon",
    "ensure_ccw",
    "ensure_cw",
    "point_on_boundary",
    "same_point",
    "segment_inside_boundaries",
]
