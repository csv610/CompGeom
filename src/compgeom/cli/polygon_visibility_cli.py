from __future__ import annotations

import math

from compgeom import EPSILON, Point2D, cross_product, is_on_segment
from compgeom import is_point_in_polygon
from ._shared import print_lines


def _dot(a: Point2D, b: Point2D) -> float:
    return a.x * b.x + a.y * b.y


def _sub(a: Point2D, b: Point2D) -> Point2D:
    return Point2D(a.x - b.x, a.y - b.y)


def _signed_area_twice(polygon: list[Point2D]) -> float:
    return sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


def _ensure_ccw(polygon: list[Point2D]) -> list[Point2D]:
    return polygon if _signed_area_twice(polygon) >= 0 else list(reversed(polygon))


def _parse_point(text: str, label: str) -> Point2D:
    parts = text.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid {label}: expected 2 numbers, got {len(parts)}.")
    x, y = map(float, parts)
    return Point2D(x, y)


def parse_input(lines: list[str]) -> tuple[Point2D, list[Point2D]]:
    cleaned = [line.strip() for line in lines if line.strip()]
    if len(cleaned) < 4:
        raise ValueError("Expected at least 4 non-empty lines: query point and 3 polygon vertices.")

    query = _parse_point(cleaned[0], "query point")
    polygon = [_parse_point(line, f"vertex {index}") for index, line in enumerate(cleaned[1:])]
    if len(polygon) < 3:
        raise ValueError("Polygon must contain at least 3 vertices.")

    polygon = _ensure_ccw(polygon)
    if abs(_signed_area_twice(polygon)) < EPSILON:
        raise ValueError("Polygon must have non-zero area.")
    return query, polygon


def _segment_parameters(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> tuple[float, float] | None:
    ab = _sub(b, a)
    cd = _sub(d, c)
    denominator = ab.x * cd.y - ab.y * cd.x
    if abs(denominator) <= EPSILON:
        return None

    ac = _sub(c, a)
    t = (ac.x * cd.y - ac.y * cd.x) / denominator
    u = (ac.x * ab.y - ac.y * ab.x) / denominator
    return t, u


def _proper_segment_intersection(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    o1 = cross_product(a, b, c)
    o2 = cross_product(a, b, d)
    o3 = cross_product(c, d, a)
    o4 = cross_product(c, d, b)

    if abs(o1) <= EPSILON and is_on_segment(c, a, b):
        return False
    if abs(o2) <= EPSILON and is_on_segment(d, a, b):
        return False
    if abs(o3) <= EPSILON and is_on_segment(a, c, d):
        return False
    if abs(o4) <= EPSILON and is_on_segment(b, c, d):
        return False
    return (o1 > EPSILON) != (o2 > EPSILON) and (o3 > EPSILON) != (o4 > EPSILON)


def _segment_sample_class(query: Point2D, target: Point2D, polygon: list[Point2D], from_inside: bool) -> bool:
    midpoint = Point2D((query.x + target.x) / 2.0, (query.y + target.y) / 2.0)
    midpoint_inside = is_point_in_polygon(midpoint, polygon)
    return midpoint_inside if from_inside else not midpoint_inside


def is_boundary_point_visible(query: Point2D, target: Point2D, polygon: list[Point2D]) -> bool:
    from_inside = is_point_in_polygon(query, polygon)
    hit_boundary = False

    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        target_on_edge = is_on_segment(target, start, end)

        if _proper_segment_intersection(query, target, start, end):
            return False

        params = _segment_parameters(query, target, start, end)
        if params is None:
            if target_on_edge and abs(cross_product(query, target, start)) <= EPSILON:
                hit_boundary = True
            continue

        t, u = params
        if EPSILON < t < 1 - EPSILON and EPSILON < u < 1 - EPSILON:
            return False
        if target_on_edge and abs(t - 1.0) <= 1e-7 and -EPSILON <= u <= 1 + EPSILON:
            hit_boundary = True

    return hit_boundary and _segment_sample_class(query, target, polygon, from_inside)


def _ray_hits_edge_parameter(query: Point2D, through: Point2D, edge_start: Point2D, edge_end: Point2D) -> float | None:
    direction = _sub(through, query)
    if abs(direction.x) <= EPSILON and abs(direction.y) <= EPSILON:
        return None

    edge = _sub(edge_end, edge_start)
    denominator = direction.x * edge.y - direction.y * edge.x
    if abs(denominator) <= EPSILON:
        return None

    delta = _sub(edge_start, query)
    ray_t = (delta.x * edge.y - delta.y * edge.x) / denominator
    edge_u = (delta.x * direction.y - delta.y * direction.x) / denominator
    if ray_t <= EPSILON:
        return None
    if edge_u < -EPSILON or edge_u > 1 + EPSILON:
        return None
    return min(max(edge_u, 0.0), 1.0)


def _dedupe_parameters(values: list[float]) -> list[float]:
    ordered = sorted(values)
    deduped: list[float] = []
    for value in ordered:
        if not deduped or abs(value - deduped[-1]) > 1e-7:
            deduped.append(value)
    return deduped


def visible_boundary_segments(query: Point2D, polygon: list[Point2D]) -> list[tuple[Point2D, Point2D]]:
    segments: list[tuple[Point2D, Point2D]] = []

    for edge_index, start in enumerate(polygon):
        end = polygon[(edge_index + 1) % len(polygon)]
        parameters = [0.0, 1.0]

        for vertex in polygon:
            split = _ray_hits_edge_parameter(query, vertex, start, end)
            if split is not None:
                parameters.append(split)

        parameters = _dedupe_parameters(parameters)
        edge_vector = _sub(end, start)

        for left, right in zip(parameters, parameters[1:]):
            if right - left <= 1e-7:
                continue

            midpoint_param = (left + right) / 2.0
            midpoint = Point2D(
                start.x + midpoint_param * edge_vector.x,
                start.y + midpoint_param * edge_vector.y,
            )
            if not is_boundary_point_visible(query, midpoint, polygon):
                continue

            left_point = Point2D(start.x + left * edge_vector.x, start.y + left * edge_vector.y)
            right_point = Point2D(start.x + right * edge_vector.x, start.y + right * edge_vector.y)
            if math.hypot(right_point.x - left_point.x, right_point.y - left_point.y) <= 1e-7:
                continue
            segments.append((left_point, right_point))

    return _merge_adjacent_segments(segments)


def _merge_adjacent_segments(segments: list[tuple[Point2D, Point2D]]) -> list[tuple[Point2D, Point2D]]:
    if not segments:
        return []

    merged: list[tuple[Point2D, Point2D]] = []
    for start, end in segments:
        if not merged:
            merged.append((start, end))
            continue

        last_start, last_end = merged[-1]
        same_line = abs(cross_product(last_start, last_end, start)) <= 1e-7 and abs(
            cross_product(last_start, last_end, end)
        ) <= 1e-7
        if same_line and last_end == start:
            merged[-1] = (last_start, end)
            continue
        merged.append((start, end))
    return merged


def format_point(point: Point2D) -> str:
    return f"({point.x:.6f}, {point.y:.6f})"


def main() -> int:
    query = Point2D(1.0, 2.5)
    polygon = [
        Point2D(0.0, 0.0),
        Point2D(5.0, 0.0),
        Point2D(5.0, 1.0),
        Point2D(2.0, 1.0),
        Point2D(2.0, 4.0),
        Point2D(5.0, 4.0),
        Point2D(5.0, 5.0),
        Point2D(0.0, 5.0),
    ]

    segments = visible_boundary_segments(query, polygon)
    if not segments:
        print("Visible Segments:")
        print("  None")
        return 0

    print("Visible Segments:")
    for index, (start, end) in enumerate(segments, start=1):
        print(f"  {index:3}: {format_point(start)} -> {format_point(end)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
