import math

import pytest

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh import PolygonMesh
from compgeom.polygon.medial_axis import (
    approximate_medial_axis,
    edge_length,
    ensure_ccw as medial_ensure_ccw,
    point_key,
    polygon_area,
    sample_polygon_boundary as medial_sample_polygon_boundary,
    segment_key,
    triangle_centroid,
)
from compgeom.polygon.planar import (
    DCEL,
    DCELFace,
    DCELHalfEdge,
    DCELVertex,
    _ensure_orientation,
    _link_cycle,
    _signed_area_twice,
    face_cycle_points,
)
from compgeom.polygon.polygon import Polygon, generate_points_in_triangle, is_ear, orient_to_cardinal, rotate_polygon
from compgeom.polygon.polygon_boolean import get_polygon_area, polygon_union
from compgeom.polygon.polygon_decomposer import (
    _TriangleView,
    _cleanup_face,
    _diagonal_crosses,
    _domain_contains_point,
    _ear_clip,
    _hertel_mehlhorn,
    _is_ear,
    _is_y_monotone,
    _mesh_from_point_faces,
    _monotone_partitions,
    _ordered_face_from_triangles,
    _point_on_segment_at_x,
    _segment_inside_domain,
    _share_triangle_edge,
    _splice_hole,
    _split_face_by_diagonal,
    _trapezoidal_faces,
    _triangulate_with_holes,
    _triangulation_with_diagonals,
    _vertical_line_intersections,
    _visibility_faces,
)
from compgeom.polygon.polygon_factory import (
    generate_random_convex_polygon,
    generate_simple_polygon,
    random_convex_points,
    random_convex_polygon,
    simple_polygon,
    simple_polygon_points,
)
from compgeom.polygon.polygon_path import segment_inside_polygon
from compgeom.polygon.polygon_polynomial import solve_linear_system
from compgeom.polygon.polygon_sampling import get_perimeter_distances
from compgeom.polygon.polygon_similarity import get_similarity_signature
from compgeom.polygon.polygon_simplification import _intersect_segments, resolve_self_intersections
from compgeom.polygon.polygon_utils import (
    cleanup_polygon,
    ensure_ccw,
    ensure_cw,
    point_on_boundary,
    rotate_polygon as rotate_polygon_utils,
    same_point,
    segment_inside_boundaries,
)


def square_vertices() -> list[Point2D]:
    return [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]


def test_polygon_utils_helpers_cover_orientation_rotation_and_cleanup():
    cw_square = [Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0)]
    ccw_square = ensure_ccw(cw_square)

    assert _signed_area_twice(ccw_square) > 0
    assert ensure_cw(ccw_square) == list(reversed(ccw_square))
    assert same_point(Point2D(1.0, 1.0), Point2D(1.0 + 1e-8, 1.0 - 1e-8))
    assert point_on_boundary(Point2D(1, 0), ccw_square) is True
    assert point_on_boundary(Point2D(3, 0), ccw_square) is False

    cleaned = cleanup_polygon(
        [Point2D(0, 0), Point2D(1, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), Point2D(0, 0)]
    )
    assert cleaned == [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]

    rotated = rotate_polygon_utils(
        [Point2D(2, 1), Point2D(1, 2), Point2D(0, 1), Point2D(1, 0)],
        math.pi / 2,
        center=Point2D(1, 1),
    )
    assert same_point(rotated[0], Point2D(1, 2))

    inside = segment_inside_boundaries(
        Point2D(0.5, 0.5),
        Point2D(1.5, 1.5),
        [ccw_square],
        lambda midpoint: Polygon(ccw_square).contains_point(midpoint),
    )
    crossing = segment_inside_boundaries(
        Point2D(-1, 1),
        Point2D(3, 1),
        [ccw_square],
        lambda midpoint: Polygon(ccw_square).contains_point(midpoint),
    )
    assert inside is True
    assert crossing is False


def test_polygon_factory_and_wrapper_helpers_generate_expected_shapes():
    convex_points = random_convex_points(8, (0, 10), (0, 10))
    simple_points = simple_polygon_points(7, (0, 10), (0, 10))
    convex_polygon = random_convex_polygon(8, (0, 10), (0, 10))
    simple_poly = simple_polygon(7, (0, 10), (0, 10))

    assert len(convex_points) >= 3
    assert len(simple_points) == 7
    assert isinstance(convex_polygon, Polygon)
    assert isinstance(simple_poly, Polygon)
    assert len(generate_random_convex_polygon(8, (0, 10), (0, 10))) >= 3
    assert len(generate_simple_polygon(7, (0, 10), (0, 10))) == 7


def test_polygon_wrapper_helpers_cover_rotation_triangle_sampling_and_ears():
    triangle = [Point2D(0, 0), Point2D(4, 0), Point2D(0, 4)]
    rotated = rotate_polygon(triangle, math.pi / 2, center=Point2D(0, 0))
    assert same_point(rotated[1], Point2D(0, 4))
    squared = orient_to_cardinal([Point2D(0, 0), Point2D(1, 1), Point2D(0, 2)], 0)
    dx = squared[1].x - squared[0].x
    dy = squared[1].y - squared[0].y
    assert abs(dx) < 1e-9 or abs(dy) < 1e-9

    convex_polygon = [Point2D(0, 0), Point2D(3, 0), Point2D(4, 2), Point2D(2, 4), Point2D(0, 3)]
    concave_polygon = [Point2D(0, 0), Point2D(3, 0), Point2D(3, 3), Point2D(1.5, 1.5), Point2D(0, 3)]
    assert is_ear(convex_polygon[-1], convex_polygon[0], convex_polygon[1], convex_polygon) is True
    assert _is_ear(concave_polygon[2], concave_polygon[3], concave_polygon[4], concave_polygon) is False

    samples_2d = generate_points_in_triangle(triangle[0], triangle[1], triangle[2], n_points=5)
    samples_3d = generate_points_in_triangle(
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 1),
        n_points=5,
    )
    assert len(samples_2d) == 5
    assert len(samples_3d) == 5
    assert all(isinstance(point, Point2D) for point in samples_2d)
    assert all(isinstance(point, Point3D) for point in samples_3d)


def test_polygon_boolean_polynomial_sampling_and_similarity_helpers():
    square = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
    shifted = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
    disjoint = [Point2D(5, 0), Point2D(7, 0), Point2D(7, 2), Point2D(5, 2)]

    overlap_union = polygon_union(square, shifted)
    disjoint_union = polygon_union(square, disjoint)
    assert Point2D(0, 0) in overlap_union
    assert len(disjoint_union) == len(square) + len(disjoint)
    assert math.isclose(get_polygon_area(square), 4.0, abs_tol=1e-9)

    matrix = [[2.0, 1.0], [1.0, 3.0]]
    rhs = [5.0, 6.0]
    solution = solve_linear_system(matrix, rhs)
    assert math.isclose(solution[0], 1.8, abs_tol=1e-9)
    assert math.isclose(solution[1], 1.4, abs_tol=1e-9)

    perimeter = get_perimeter_distances(square)
    assert perimeter == [0.0, 2.0, 4.0, 6.0, 8.0]

    signature = get_similarity_signature(Polygon(square))
    assert signature is not None
    assert len(signature) == 4
    assert get_similarity_signature(Polygon([Point2D(0, 0), Point2D(0, 0)])) is None


def test_medial_axis_helpers_cover_geometry_keys_and_sampling():
    triangle = [Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)]
    clockwise = list(reversed(triangle))

    assert math.isclose(polygon_area(triangle), 2.0, abs_tol=1e-9)
    assert medial_ensure_ccw(clockwise) == triangle
    assert math.isclose(edge_length(Point2D(0, 0), Point2D(3, 4)), 5.0, abs_tol=1e-9)
    assert triangle_centroid(tuple(triangle)) == Point2D(2 / 3, 2 / 3)
    assert point_key(Point2D(0.0, 0.0)) == point_key(Point2D(0.0, 0.0))
    assert segment_key(Point2D(0, 0), Point2D(1, 1)) == segment_key(Point2D(1, 1), Point2D(0, 0))

    samples = medial_sample_polygon_boundary(triangle, max_segment_length=0.5)
    assert len(samples) > len(triangle)

    medial_axis = approximate_medial_axis([Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)], 0.75)
    assert "samples" in medial_axis
    assert "centers" in medial_axis
    assert "segments" in medial_axis


def test_planar_primitives_and_cycle_helpers_have_direct_coverage():
    points = [Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)]
    face = DCELFace(id=10)
    vertices, interior, exterior = _link_cycle(face, points)

    assert isinstance(vertices[0], DCELVertex)
    assert isinstance(interior[0], DCELHalfEdge)
    assert isinstance(DCEL(vertices, interior + exterior, [face]), DCEL)
    assert interior[0].destination == interior[1].origin
    assert face_cycle_points(face.outer_component) == points
    assert _ensure_orientation(list(reversed(points)), ccw=True) == points


def test_polygon_simplification_helpers_cover_intersection_and_resolution():
    intersection = _intersect_segments(Point2D(0, 0), Point2D(2, 2), Point2D(0, 2), Point2D(2, 0))
    assert intersection == Point2D(1, 1)

    bowtie = Polygon([Point2D(0, 0), Point2D(2, 2), Point2D(0, 2), Point2D(2, 0)])
    simple = resolve_self_intersections(bowtie)
    assert len(simple) >= 3
    assert all(isinstance(point, Point2D) for point in simple)


def test_polygon_decomposer_private_helpers_cover_remaining_paths():
    concave = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
    outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
    hole = [Point2D(2, 2), Point2D(2, 4), Point2D(4, 4), Point2D(4, 2)]

    triangle_view = _TriangleView(*concave[:3])
    assert triangle_view.vertices == tuple(concave[:3])

    triangles, diagonals, ordered = _ear_clip(concave, collect_diagonals=True)
    assert triangles
    assert ordered == ensure_ccw(concave)
    assert diagonals
    assert _triangulation_with_diagonals(concave) == (triangles, diagonals, ordered)

    triangles_with_holes, merged_vertices = _triangulate_with_holes(outer, [hole])
    assert triangles_with_holes
    assert len(merged_vertices) > len(outer)

    partitions, hm_vertices = _hertel_mehlhorn(concave)
    assert partitions
    assert hm_vertices == ordered

    assert _domain_contains_point(outer, [hole], Point2D(1, 1)) is True
    assert _domain_contains_point(outer, [hole], Point2D(3, 3)) is False
    assert _segment_inside_domain(outer, [hole], Point2D(1, 1), Point2D(1, 5)) is True
    assert _segment_inside_domain(outer, [hole], Point2D(1, 3), Point2D(5, 3)) is False

    spliced = _splice_hole(outer, hole)
    assert len(spliced) > len(outer) + len(hole)

    mesh = _mesh_from_point_faces(
        [
            [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1)],
            [Point2D(0, 0), Point2D(1, 1), Point2D(0, 1)],
        ]
    )
    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) == 2

    ordered_face = _ordered_face_from_triangles([(0, 1, 2), (0, 2, 3)], square_vertices())
    assert ordered_face == (0, 1, 2, 3)
    assert _is_y_monotone((0, 1, 2, 3), square_vertices()) is True
    assert _is_y_monotone((0, 1, 2, 3, 4), [Point2D(0, 0), Point2D(2, 2), Point2D(4, 0), Point2D(3, 4), Point2D(1, 4)]) is False

    assert _share_triangle_edge([(0, 1, 2)], [(1, 2, 3)]) is True
    monotone_parts = _monotone_partitions([(0, 1, 2), (0, 2, 3)], square_vertices())
    assert monotone_parts == [(0, 1, 2, 3)]

    assert _point_on_segment_at_x(Point2D(0, 0), Point2D(2, 2), 1.0) == Point2D(1.0, 1.0)
    assert _point_on_segment_at_x(Point2D(1, 0), Point2D(1, 2), 1.0) == Point2D(1.0, 0.0)

    hits = _vertical_line_intersections([Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)], 2.0)
    assert hits == [(0.0, 0), (4.0, 2)]

    assert _cleanup_face([Point2D(0, 0), Point2D(1, 0), Point2D(1, 0), Point2D(0, 0)]) == [Point2D(0, 0), Point2D(1, 0)]

    trapezoids = _trapezoidal_faces([Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)])
    assert trapezoids == [[Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]]

    assert _diagonal_crosses((0, 2), [(1, 3)], square_vertices()) is True
    assert _split_face_by_diagonal((0, 1, 2, 3), (0, 2)) == [(0, 1, 2), (2, 3, 0)]

    visibility_faces = _visibility_faces(concave)
    assert visibility_faces
    assert sum(len(face) for face in visibility_faces) >= len(concave)


def test_segment_inside_polygon_private_wrapper_is_exercised_directly():
    polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
    assert segment_inside_polygon(polygon, Point2D(1, 1), Point2D(3, 3)) is True
    assert segment_inside_polygon(polygon, Point2D(-1, 1), Point2D(3, 1)) is False
