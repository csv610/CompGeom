from __future__ import annotations

from compgeom.kernel import EPSILON, Point2D
from compgeom.polygon.polygon import Polygon


def trapezoidal_decompose_polygon(polygon: list[Point2D]) -> list[list[Point2D]]:
    """Decomposes a simple polygon into trapezoids."""
    if len(polygon) < 3:
        return [list(polygon)]
    ordered = Polygon(polygon).ensure_ccw().as_list()

    x_values = sorted({point.x for point in ordered})
    if len(x_values) < 2:
        return [ordered]

    faces: list[list[Point2D]] = []
    for left_x, right_x in zip(x_values, x_values[1:]):
        if right_x - left_x <= EPSILON:
            continue
        mid_x = (left_x + right_x) / 2.0
        intersections = _vertical_line_intersections(ordered, mid_x)
        for lower_hit, upper_hit in zip(intersections[0::2], intersections[1::2]):
            _, lower_edge_index = lower_hit
            _, upper_edge_index = upper_hit
            lower_start = ordered[lower_edge_index]
            lower_end = ordered[(lower_edge_index + 1) % len(ordered)]
            upper_start = ordered[upper_edge_index]
            upper_end = ordered[(upper_edge_index + 1) % len(ordered)]

            lower_left = _point_on_segment_at_x(lower_start, lower_end, left_x)
            lower_right = _point_on_segment_at_x(lower_start, lower_end, right_x)
            upper_left = _point_on_segment_at_x(upper_start, upper_end, left_x)
            upper_right = _point_on_segment_at_x(upper_start, upper_end, right_x)
            if None in (lower_left, lower_right, upper_left, upper_right):
                continue

            face = _cleanup_face([lower_left, lower_right, upper_right, upper_left])
            if len(face) >= 3:
                faces.append(face)

    return faces or [ordered]


def _vertical_line_intersections(
    polygon: list[Point2D], x: float
) -> list[tuple[float, int]]:
    hits: list[tuple[float, int]] = []
    n = len(polygon)
    for i in range(n):
        start = polygon[i]
        end = polygon[(i + 1) % n]
        if abs(start.x - end.x) <= EPSILON:
            continue
        min_x = min(start.x, end.x)
        max_x = max(start.x, end.x)
        if x < min_x - EPSILON or x >= max_x - EPSILON:
            continue
        point = _point_on_segment_at_x(start, end, x)
        if point is not None:
            hits.append((point.y, i))
    hits.sort(key=lambda item: item[0])
    return hits


def _point_on_segment_at_x(start: Point2D, end: Point2D, x: float) -> Point2D | None:
    """
    Compute the point on a segment at a given x-coordinate.
    Returns None if x is outside the segment's x-range.
    """
    min_x = min(start.x, end.x) - EPSILON
    max_x = max(start.x, end.x) + EPSILON
    if x < min_x or x > max_x:
        return None
    if abs(end.x - start.x) <= EPSILON:
        if abs(start.x - x) > EPSILON:
            return None
        return Point2D(x, start.y)

    t = (x - start.x) / (end.x - start.x)
    y = start.y + t * (end.y - start.y)
    return Point2D(x, y)


def _cleanup_face(points: list[Point2D]) -> list[Point2D]:
    face: list[Point2D] = []
    for point in points:
        if face and point == face[-1]:
            continue
        face.append(point)
    if len(face) > 1 and face[0] == face[-1]:
        face.pop()
    return face
