"""Constrained Delaunay Triangulation (CDT)."""

from __future__ import annotations
from ....kernel import EPSILON, Point2D, incircle_sign, is_on_segment, orientation_sign


def _point_key(point: Point2D):
    return (round(point.x / EPSILON), round(point.y / EPSILON), point.id)


def _edge_key(a: Point2D, b: Point2D):
    return tuple(sorted((_point_key(a), _point_key(b))))


def _make_ccw_triangle(a: Point2D, b: Point2D, c: Point2D):
    return (a, b, c) if orientation_sign(a, b, c) >= 0 else (a, c, b)


def _build_edge_map(triangles):
    edge_map = {}
    for triangle_index, triangle in enumerate(triangles):
        for edge in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            edge_map.setdefault(_edge_key(*edge), []).append(triangle_index)
    return edge_map


def _quadrilateral_for_edge(first, second, shared_edge_key):
    shared_keys = set(shared_edge_key)
    first_opposite = next(vertex for vertex in first if _point_key(vertex) not in shared_keys)
    second_opposite = next(vertex for vertex in second if _point_key(vertex) not in shared_keys)
    shared_vertices = [vertex for vertex in first if _point_key(vertex) in shared_keys]
    a, b = shared_vertices
    return a, b, first_opposite, second_opposite


def _should_flip_constrained_edge(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    if orientation_sign(c, a, d) == 0 or orientation_sign(c, d, b) == 0:
        return False
    if orientation_sign(c, a, b) == 0 or orientation_sign(d, a, b) == 0:
        return False
    if orientation_sign(c, a, d) < 0:
        a, d = d, a
    if orientation_sign(c, d, b) < 0:
        c, b = b, c
    if orientation_sign(c, d, a) == 0 or orientation_sign(c, d, b) == 0:
        return False
    return incircle_sign(c, a, d, b) > 0 or incircle_sign(c, d, b, a) > 0


def _point_on_boundary(point: Point2D, boundary: list[Point2D]) -> bool:
    return any(is_on_segment(point, boundary[index], boundary[(index + 1) % len(boundary)]) for index in range(len(boundary)))


def _proper_segment_intersection(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    o1 = orientation_sign(a, b, c)
    o2 = orientation_sign(a, b, d)
    o3 = orientation_sign(c, d, a)
    o4 = orientation_sign(c, d, b)

    if o1 == 0 and is_on_segment(c, a, b):
        return False
    if o2 == 0 and is_on_segment(d, a, b):
        return False
    if o3 == 0 and is_on_segment(a, c, d):
        return False
    if o4 == 0 and is_on_segment(b, c, d):
        return False
    return o1 != o2 and o3 != o4


def _point_in_domain(point: Point2D, outer_boundary: list[Point2D], holes: list[list[Point2D]]) -> bool:
    from ....polygon.polygon_metrics import is_point_in_polygon
    if not is_point_in_polygon(point, outer_boundary):
        return False
    for hole in holes:
        if is_point_in_polygon(point, hole) and not _point_on_boundary(point, hole):
            return False
    return True


def _segment_valid_in_domain(
    start: Point2D,
    end: Point2D,
    outer_boundary: list[Point2D],
    holes: list[list[Point2D]],
    constrained_segments: set,
) -> bool:
    midpoint = Point2D((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not _point_in_domain(midpoint, outer_boundary, holes):
        return False

    for boundary in [outer_boundary, *holes]:
        for index, edge_start in enumerate(boundary):
            edge_end = boundary[(index + 1) % len(boundary)]
            if start == edge_start or start == edge_end or end == edge_start or end == edge_end:
                continue
            if _proper_segment_intersection(start, end, edge_start, edge_end):
                return False
    return True


def constrained_delaunay_triangulation(outer_boundary: list[Point2D], holes: list[list[Point2D]] | None = None):
    from ....polygon.polygon import triangulate_polygon_with_holes
    holes = holes or []
    triangles, merged_polygon = triangulate_polygon_with_holes(outer_boundary, holes)
    constrained_edges = {
        _edge_key(merged_polygon[index], merged_polygon[(index + 1) % len(merged_polygon)])
        for index in range(len(merged_polygon))
    }

    changed = True
    while changed:
        changed = False
        edge_map = _build_edge_map(triangles)
        for edge_key, owners in edge_map.items():
            if edge_key in constrained_edges or len(owners) != 2:
                continue

            first_index = owners[0]
            second_index = owners[1]
            first = triangles[first_index]
            second = triangles[second_index]
            a, b, c, d = _quadrilateral_for_edge(first, second, edge_key)
            if orientation_sign(c, d, a) == 0 or orientation_sign(c, d, b) == 0:
                continue
            if not _segment_valid_in_domain(c, d, outer_boundary, holes, constrained_edges):
                continue
            if not _should_flip_constrained_edge(a, b, c, d):
                continue

            replacement_one = _make_ccw_triangle(c, d, a)
            replacement_two = _make_ccw_triangle(c, b, d)
            triangles[first_index] = replacement_one
            triangles[second_index] = replacement_two
            changed = True
            break

    return triangles, constrained_edges
