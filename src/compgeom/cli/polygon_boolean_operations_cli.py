from __future__ import annotations

import argparse
import sys

from compgeom import EPSILON, Point2D, length, sub
from compgeom.polygon import is_point_in_polygon
from ._shared import read_input_lines, parse_points
from .line_arrangement_cli import analyze_arrangement


def signed_area(polygon):
    return 0.5 * sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


def ensure_ccw(polygon):
    return polygon if signed_area(polygon) >= 0 else list(reversed(polygon))


def centroid(polygon):
    area = signed_area(polygon)
    if abs(area) <= EPSILON:
        x = sum(point.x for point in polygon) / len(polygon)
        y = sum(point.y for point in polygon) / len(polygon)
        return Point2D(x, y)

    scale = 1.0 / (6.0 * area)
    cx = 0.0
    cy = 0.0
    for i, p1 in enumerate(polygon):
        p2 = polygon[(i + 1) % len(polygon)]
        cross = p1.x * p2.y - p2.x * p1.y
        cx += (p1.x + p2.x) * cross
        cy += (p1.y + p2.y) * cross
    return Point2D(cx * scale, cy * scale)


def representative_point(polygon):
    center = centroid(polygon)
    if is_point_in_polygon(center, polygon):
        return center

    p0 = polygon[0]
    p1 = polygon[1]
    midpoint = Point2D((p0.x + p1.x) / 2.0, (p0.y + p1.y) / 2.0)
    edge = sub(p1, p0)
    edge_length = length(edge)
    if edge_length <= EPSILON:
        return midpoint

    inward = Point2D(-edge.y / edge_length, edge.x / edge_length)
    offset = max(edge_length * 1e-6, 1e-6)
    probe = Point2D(midpoint.x + inward.x * offset, midpoint.y + inward.y * offset)
    if is_point_in_polygon(probe, polygon):
        return probe
    return Point2D(midpoint.x - inward.x * offset, midpoint.y - inward.y * offset)


def polygon_edges(polygon):
    polygon = ensure_ccw(list(polygon))
    return [(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon))]


def point_key(point):
    return (round(point.x / EPSILON), round(point.y / EPSILON))


def segment_parameter(point, start, end):
    dx = end.x - start.x
    dy = end.y - start.y
    if abs(dx) >= abs(dy):
        return 0.0 if abs(dx) < EPSILON else (point.x - start.x) / dx
    return 0.0 if abs(dy) < EPSILON else (point.y - start.y) / dy


def segment_intersection_points(seg1, seg2):
    a, b = seg1
    c, d = seg2
    ab = sub(b, a)
    cd = sub(d, c)
    denominator = ab.x * cd.y - ab.y * cd.x
    ac = sub(c, a)

    if abs(denominator) > EPSILON:
        t = (ac.x * cd.y - ac.y * cd.x) / denominator
        u = (ac.x * ab.y - ac.y * ab.x) / denominator
        if -EPSILON <= t <= 1 + EPSILON and -EPSILON <= u <= 1 + EPSILON:
            return [Point2D(a.x + t * ab.x, a.y + t * ab.y)]
        return []

    if abs((c.x - a.x) * ab.y - (c.y - a.y) * ab.x) > EPSILON:
        return []

    overlap_points = []
    for point in (a, b, c, d):
        if point_on_segment(point, a, b) and point_on_segment(point, c, d):
            overlap_points.append(point)

    unique = {}
    for point in overlap_points:
        unique[point_key(point)] = point
    return list(unique.values())


def point_on_segment(point, start, end):
    cross = abs(
        (end.x - start.x) * (point.y - start.y)
        - (end.y - start.y) * (point.x - start.x)
    )
    if cross > EPSILON:
        return False
    return (
        min(start.x, end.x) - EPSILON <= point.x <= max(start.x, end.x) + EPSILON
        and min(start.y, end.y) - EPSILON <= point.y <= max(start.y, end.y) + EPSILON
    )


def split_polygon_edges_against_other(polygon_edges_a, polygon_edges_b):
    split_segments = []
    intersections = {}

    for edge in polygon_edges_a:
        start, end = edge
        split_points = {point_key(start): start, point_key(end): end}
        for other_edge in polygon_edges_b:
            for point in segment_intersection_points(edge, other_edge):
                split_points[point_key(point)] = point
                intersections[point_key(point)] = point

        ordered = sorted(
            split_points.values(),
            key=lambda point: segment_parameter(point, start, end),
        )
        for left, right in zip(ordered, ordered[1:]):
            if length(sub(right, left)) > EPSILON:
                split_segments.append((left, right))

    return split_segments, intersections


def point_in_polygon_strict(point, polygon):
    return is_point_in_polygon(point, polygon)


def polygon_key(polygon):
    coords = [(round(point.x / EPSILON), round(point.y / EPSILON)) for point in polygon]
    candidates = []
    for sequence in (coords, list(reversed(coords))):
        start = min(range(len(sequence)), key=sequence.__getitem__)
        candidates.append(tuple(sequence[start:] + sequence[:start]))
    return min(candidates)


def deduplicate_polygons(polygons):
    unique = {}
    for polygon in polygons:
        unique[polygon_key(polygon)] = polygon
    return list(unique.values())


def make_region(outer, holes=None):
    return {
        "outer": ensure_ccw(list(outer)),
        "holes": [list(reversed(hole)) for hole in (holes or [])],
    }


def region_key(region):
    return (
        polygon_key(region["outer"]),
        tuple(sorted(polygon_key(hole) for hole in region["holes"])),
    )


def deduplicate_regions(regions):
    unique = {}
    for region in regions:
        unique[region_key(region)] = region
    return list(unique.values())


def polygons_disjoint(poly1, poly2):
    return not any(is_point_in_polygon(vertex, poly2) for vertex in poly1) and not any(
        is_point_in_polygon(vertex, poly1) for vertex in poly2
    )


def handle_no_intersection_case(operation, poly1, poly2):
    poly1_in_poly2 = all(is_point_in_polygon(vertex, poly2) for vertex in poly1)
    poly2_in_poly1 = all(is_point_in_polygon(vertex, poly1) for vertex in poly2)

    if polygons_disjoint(poly1, poly2):
        if operation == "intersection":
            return []
        if operation == "union":
            return [make_region(poly1), make_region(poly2)]
        if operation == "difference":
            return [make_region(poly1)]
        if operation == "xor":
            return [make_region(poly1), make_region(poly2)]

    if poly1_in_poly2:
        if operation == "intersection":
            return [make_region(poly1)]
        if operation == "union":
            return [make_region(poly2)]
        if operation == "difference":
            return []
        if operation == "xor":
            return [make_region(poly2, [poly1])]

    if poly2_in_poly1:
        if operation == "intersection":
            return [make_region(poly2)]
        if operation == "union":
            return [make_region(poly1)]
        if operation == "difference":
            return [make_region(poly1, [poly2])]
        if operation == "xor":
            return [make_region(poly1, [poly2])]

    return None


def segment_midpoint(segment):
    start, end = segment
    return Point2D((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)


def segment_angle(start, end):
    return __import__("math").atan2(end.y - start.y, end.x - start.x)


def build_boundary_segments(poly1, poly2, operation):
    edges1 = polygon_edges(poly1)
    edges2 = polygon_edges(poly2)
    split1, intersections1 = split_polygon_edges_against_other(edges1, edges2)
    split2, intersections2 = split_polygon_edges_against_other(edges2, edges1)
    intersections = {**intersections1, **intersections2}

    special = None
    if not intersections:
        special = handle_no_intersection_case(operation, poly1, poly2)
        if special is not None:
            return None, special

    directed = []
    for segment in split1:
        midpoint = segment_midpoint(segment)
        inside_other = is_point_in_polygon(midpoint, poly2)
        if operation == "intersection" and inside_other:
            directed.append(segment)
        elif operation in {"union", "xor", "difference"} and not inside_other:
            directed.append(segment)

    for segment in split2:
        midpoint = segment_midpoint(segment)
        inside_other = is_point_in_polygon(midpoint, poly1)
        if operation == "intersection" and inside_other:
            directed.append(segment)
        elif operation == "union" and not inside_other:
            directed.append(segment)
        elif operation == "xor" and not inside_other:
            directed.append(segment)
        elif operation == "difference" and inside_other:
            directed.append((segment[1], segment[0]))

    return directed, None


def trace_directed_loops(directed_segments):
    adjacency = {}
    vertices = {}
    for start, end in directed_segments:
        start_key = point_key(start)
        end_key = point_key(end)
        vertices[start_key] = start
        vertices[end_key] = end
        adjacency.setdefault(start_key, []).append(end_key)

    used = set()
    polygons = []
    for start, end in directed_segments:
        start_key = point_key(start)
        end_key = point_key(end)
        edge_key = (start_key, end_key)
        if edge_key in used:
            continue

        polygon = []
        current_start = start_key
        current_end = end_key
        while True:
            used.add((current_start, current_end))
            polygon.append(vertices[current_start])

            candidates = [
                candidate
                for candidate in adjacency.get(current_end, [])
                if (current_end, candidate) not in used
            ]
            if not candidates:
                break

            incoming_angle = segment_angle(
                vertices[current_start], vertices[current_end]
            )
            next_end = min(
                candidates,
                key=lambda candidate: (
                    (
                        segment_angle(vertices[current_end], vertices[candidate])
                        - incoming_angle
                    )
                    % (2.0 * 3.141592653589793)
                ),
            )
            current_start, current_end = current_end, next_end
            if (current_start, current_end) == edge_key:
                break

        if len(polygon) >= 3 and length(sub(polygon[0], polygon[-1])) > EPSILON:
            area = signed_area(polygon)
            if abs(area) > EPSILON:
                polygons.append(polygon if area > 0 else list(reversed(polygon)))

    return deduplicate_polygons(polygons)


def apply_boolean_operation(poly1, poly2, operation):
    operation = operation.lower()
    if operation not in {"intersection", "union", "difference", "xor"}:
        raise ValueError(f"Unsupported operation: {operation}")

    poly1 = ensure_ccw(list(poly1))
    poly2 = ensure_ccw(list(poly2))
    if operation == "xor":
        intersections, _, arrangement_faces = analyze_arrangement(
            polygon_edges(poly1) + polygon_edges(poly2)
        )
        if not intersections:
            special = handle_no_intersection_case(operation, poly1, poly2)
            if special is not None:
                return deduplicate_regions(special)

        result = []
        for face in arrangement_faces:
            sample = representative_point(face)
            in_poly1 = point_in_polygon_strict(sample, poly1)
            in_poly2 = point_in_polygon_strict(sample, poly2)
            if in_poly1 != in_poly2:
                result.append(make_region(face))
        return deduplicate_regions(result)

    boundary_segments, special = build_boundary_segments(poly1, poly2, operation)
    if special is not None:
        return deduplicate_regions(special)
    return deduplicate_regions(
        [make_region(polygon) for polygon in trace_directed_loops(boundary_segments)]
    )


def format_point(point):
    return f"({point.x:.6f}, {point.y:.6f})"


def parse_polygon(lines, unused_arg=0):
    from ._shared import parse_points
    from compgeom.polygon import Polygon

    if lines and len(lines) > 0:
        first = lines[0]
        if first == "" or first == "4":
            valid_lines = [l for l in lines if l and l != "4"]
            points = parse_points(valid_lines)
            return Polygon(points).ensure_ccw().vertices

    points = parse_points(lines)
    return Polygon(points).ensure_ccw().vertices


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply a boolean operation to two polygons."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument(
        "--operation",
        choices=["intersection", "union", "difference", "xor"],
        default="union",
        help="Boolean operation to evaluate.",
    )
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print(
            "Error: No input provided via stdin. Provide two polygons separated by 'NEXT'."
        )
        return 1

    poly_lines_a = []
    poly_lines_b = []
    current = poly_lines_a
    for line in lines:
        if line.strip().upper() == "NEXT":
            current = poly_lines_b
            continue
        current.append(line)

    if not poly_lines_b:
        print("Error: Provide two polygons separated by 'NEXT' line.")
        return 1

    poly1 = parse_points(poly_lines_a)
    poly2 = parse_points(poly_lines_b)

    if len(poly1) < 3 or len(poly2) < 3:
        print("Error: Both polygons must have at least 3 vertices.")
        return 1

    operation = args.operation
    try:
        result = apply_boolean_operation(poly1, poly2, operation)
    except (ValueError, IndexError) as e:
        print(f"Error applying operation: {e}")
        return 1

    print(f"Operation: {operation}")
    print(f"Result regions: {len(result)}")
    for idx, region in enumerate(result, start=1):
        outer_vertices = ", ".join(format_point(point) for point in region["outer"])
        print(f"Region {idx:3} outer [CCW]: {outer_vertices}")
        for hole_idx, hole in enumerate(region["holes"], start=1):
            hole_vertices = ", ".join(format_point(point) for point in hole)
            print(f"  hole {hole_idx}: {hole_vertices}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
