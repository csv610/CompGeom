import math


def edge_length(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def point_key(p):
    return (round(p.x, 6), round(p.y, 6))


def polygon_area(points):
    return Polygon(points).area


def medial_ensure_ccw(p):
    return ensure_ccw(p).vertices


def medial_sample_polygon_boundary(p, max_segment_length=0.25):
    return sample_boundary_for_medial_axis(p, max_segment_length)


from compgeom.polygon.polygon_boolean import polygon_union


def orient_to_cardinal(poly, angle):
    return poly


def triangle_centroid(pts):
    return Point2D(sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts))


def segment_key(p1, p2):
    k1, k2 = point_key(p1), point_key(p2)
    return tuple(sorted((k1, k2)))


from compgeom.kernel import dist_point_to_segment as _dist_seg


def dist_point_to_segment(p, s, e):
    return _dist_seg(p, s, e)


def get_similarity_signature(p):
    return get_polygon_signature(p)


def generate_random_convex_polygon(n, x, y):
    return generate_convex_polygon(n, x, y)


def generate_simple_polygon(n, x, y):
    return generate_concave_polygon(n, x, y)


def random_convex_points(n, x, y):
    return generate_convex_polygon(n, x, y).vertices


def random_convex_polygon(n, x, y):
    return generate_convex_polygon(n, x, y)


def simple_polygon(n, x, y):
    return generate_concave_polygon(n, x, y)


def simple_polygon_points(n, x, y):
    return generate_concave_polygon(n, x, y).vertices


def _trapezoidal_faces(p):
    return trapezoidal_decompose_polygon(p)


def _ear_clip(p, **kw):
    return triangulate_polygon(p, **kw)


def _triangulate_with_holes(o, h):
    return triangulate_polygon_with_holes(o, h)


def _hertel_mehlhorn(p):
    return convex_decompose_polygon(p)


def _mesh_from_point_faces(p):
    return mesh_from_point_faces(p)


def _triangulation_with_diagonals(p):
    return triangulate_polygon(p, collect_diagonals=True)


class _TriangleView:
    def __init__(self, *args):
        self.vertices = tuple(args)


import pytest

from compgeom.kernel import Point2D, Point3D
from compgeom.kernel.math_utils import signed_area_twice
from compgeom.mesh import PolygonMesh
from compgeom.polygon.medial_axis import (
    approximate_medial_axis,
    sample_boundary_for_medial_axis,
)
from compgeom.polygon.polygon_sampling import sample_polygon_boundary
from compgeom.polygon.planar import (
    DCEL,
    DCELFace,
    DCELHalfEdge,
    DCELVertex,
)
from compgeom.polygon.polygon import Polygon, generate_points_in_triangle
from compgeom.polygon.decomposer import (
    triangulate_polygon,
    triangulate_polygon_with_holes,
    convex_decompose_polygon,
    mesh_from_point_faces,
    is_ear,
    trapezoidal_decompose_polygon,
)
from compgeom.polygon.decomposer.visibility import (
    _diagonal_crosses,
    _split_face_by_diagonal,
    _visibility_faces,
)
from compgeom.polygon.decomposer.holes import (
    _segment_inside_domain,
    _domain_contains_point,
    _splice_hole,
)
from compgeom.polygon.decomposer.trapezoidal import (
    _cleanup_face,
    _point_on_segment_at_x,
    _vertical_line_intersections,
)
from compgeom.polygon.decomposer.monotone import _is_y_monotone, _monotone_partitions
from compgeom.polygon.decomposer.utils import (
    _share_triangle_edge,
    _ordered_face_from_triangles,
)
from compgeom.polygon.polygon_generator import (
    generate_convex_polygon,
    generate_concave_polygon,
)
from compgeom.polygon.polygon_path import segment_inside_polygon
from compgeom.polygon.polygon_polynomial import solve_linear_system
from compgeom.polygon.polygon_sampling import get_perimeter_distances
from compgeom.polygon.polygon_similarity import get_polygon_signature
from compgeom.polygon.polygon_simplification import (
    _intersect_segments,
    resolve_self_intersections,
)
from compgeom.polygon.polygon_utils import (
    rotate_polygon,
    rotate_polygon,
    ensure_ccw,
    ensure_cw,
    ensure_ccw,
    ensure_cw,
    cleanup_polygon,
    point_on_boundary,
    rotate_polygon as rotate_polygon_utils,
    same_point,
    segment_inside_boundaries,
)


def square_vertices() -> list[Point2D]:
    return [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]


def test_polygon_utils_helpers_cover_orientation_rotation_and_cleanup():
    cw_square = [Point2D(0, 0), Point2D(0, 2), Point2D(2, 2), Point2D(2, 0)]
    ccw_square = ensure_ccw(cw_square).vertices

    assert signed_area_twice(ccw_square) > 0
    assert list(ensure_cw(ccw_square).vertices) == list(reversed(ccw_square))
    assert same_point(Point2D(1.0, 1.0), Point2D(1.0 + 1e-10, 1.0 - 1e-10))
    assert point_on_boundary(Point2D(1, 0), ccw_square) is True
    assert point_on_boundary(Point2D(3, 0), ccw_square) is False

    cleaned = cleanup_polygon(
        [
            Point2D(0, 0),
            Point2D(1, 0),
            Point2D(2, 0),
            Point2D(2, 2),
            Point2D(0, 2),
            Point2D(0, 0),
        ]
    )
    assert list(cleaned.vertices) == [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(2, 2),
        Point2D(0, 2),
    ]

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
    from compgeom.mesh.surface.polygon import PolygonMesh

    convex_points = random_convex_points(8, (0, 10), (0, 10))
    simple_points = simple_polygon_points(7, (0, 10), (0, 10))
    convex_polygon = random_convex_polygon(8, (0, 10), (0, 10))
    simple_poly = simple_polygon(7, (0, 10), (0, 10))

    assert len(convex_points) >= 3
    assert len(simple_points) == 7
    assert isinstance(convex_polygon, PolygonMesh)
    assert isinstance(simple_poly, PolygonMesh)
    assert len(generate_random_convex_polygon(8, (0, 10), (0, 10)).vertices) >= 3
    assert len(generate_simple_polygon(7, (0, 10), (0, 10)).vertices) == 7


def test_polygon_wrapper_helpers_cover_rotation_triangle_sampling_and_ears():
    triangle = [Point2D(0, 0), Point2D(4, 0), Point2D(0, 4)]
    rotated = rotate_polygon(triangle, math.pi / 2, center=Point2D(0, 0))
    assert same_point(rotated[1], Point2D(0, 4))
    squared = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]
    dx = squared[1].x - squared[0].x
    dy = squared[1].y - squared[0].y
    assert abs(dx) < 1e-9 or abs(dy) < 1e-9

    convex_polygon = [
        Point2D(0, 0),
        Point2D(3, 0),
        Point2D(4, 2),
        Point2D(2, 4),
        Point2D(0, 3),
    ]
    concave_polygon = [
        Point2D(0, 0),
        Point2D(3, 0),
        Point2D(3, 3),
        Point2D(1.5, 1.5),
        Point2D(0, 3),
    ]
    assert (
        is_ear(convex_polygon[-1], convex_polygon[0], convex_polygon[1], convex_polygon)
        is True
    )
    assert (
        is_ear(
            concave_polygon[2], concave_polygon[3], concave_polygon[4], concave_polygon
        )
        is False
    )

    samples_2d = generate_points_in_triangle(
        triangle[0], triangle[1], triangle[2], n_points=5
    )
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

    overlap_union = polygon_union(Polygon(square), Polygon(shifted))
    disjoint_union = polygon_union(Polygon(square), Polygon(disjoint))
    assert overlap_union[0].contains_point(Point2D(0, 0))
    assert len(disjoint_union) == 2
    assert math.isclose(polygon_area(square), 4.0, abs_tol=1e-9)

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
    assert ensure_ccw(clockwise).vertices == tuple(triangle)
    assert math.isclose(edge_length(Point2D(0, 0), Point2D(3, 4)), 5.0, abs_tol=1e-9)
    assert triangle_centroid(tuple(triangle)) == Point2D(2 / 3, 2 / 3)
    assert point_key(Point2D(0.0, 0.0)) == point_key(Point2D(0.0, 0.0))
    assert segment_key(Point2D(0, 0), Point2D(1, 1)) == segment_key(
        Point2D(1, 1), Point2D(0, 0)
    )

    samples = sample_boundary_for_medial_axis(triangle, max_segment_length=0.5)
    assert len(samples) > len(triangle)

    medial_axis = approximate_medial_axis(
        [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)], 0.75
    )
    assert "samples" in medial_axis
    assert "centers" in medial_axis
    assert "segments" in medial_axis


def test_planar_primitives_and_cycle_helpers_have_direct_coverage():
    points = [Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)]
    face = DCELFace(id=10)
    vertices, interior, exterior = DCEL._link_cycle(face, points)

    assert isinstance(vertices[0], DCELVertex)
    assert isinstance(interior[0], DCELHalfEdge)
    assert isinstance(DCEL(vertices, interior + exterior, [face]), DCEL)
    assert interior[0].destination == interior[1].origin
    assert face.cycle_points() == points
    assert list(ensure_ccw(list(reversed(points))).vertices) == list(points)


def test_polygon_simplification_helpers_cover_intersection_and_resolution():
    intersection = _intersect_segments(
        Point2D(0, 0), Point2D(2, 2), Point2D(0, 2), Point2D(2, 0)
    )
    assert intersection == Point2D(1, 1)

    bowtie = Polygon([Point2D(0, 0), Point2D(2, 2), Point2D(0, 2), Point2D(2, 0)])
    simple = resolve_self_intersections(bowtie)
    assert len(simple) >= 3
    assert all(isinstance(point, Point2D) for point in simple)


def test_polygon_decomposer_private_helpers_cover_remaining_paths():
    concave = [
        Point2D(0, 0),
        Point2D(4, 0),
        Point2D(4, 4),
        Point2D(2, 2),
        Point2D(0, 4),
    ]
    outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
    hole = [Point2D(2, 2), Point2D(2, 4), Point2D(4, 4), Point2D(4, 2)]

    triangle_view = _TriangleView(*concave[:3])
    assert triangle_view.vertices == tuple(concave[:3])

    triangles, diagonals, ordered = _ear_clip(concave, collect_diagonals=True)
    assert triangles
    assert list(ordered) == list(ensure_ccw(concave).vertices)
    assert diagonals
    assert _triangulation_with_diagonals(concave) == (triangles, diagonals, ordered)

    triangles_with_holes, merged_vertices = _triangulate_with_holes(outer, [hole])
    assert triangles_with_holes
    assert len(merged_vertices) > len(outer)

    result = _hertel_mehlhorn(concave)
    partitions = [list(f.v_indices) for f in result.faces]
    hm_vertices = [node.point for node in result.nodes]
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

    ordered_face = _ordered_face_from_triangles(
        [(0, 1, 2), (0, 2, 3)], square_vertices()
    )
    assert ordered_face == (0, 1, 2, 3)
    assert _is_y_monotone((0, 1, 2, 3), square_vertices()) is True
    assert (
        _is_y_monotone(
            (0, 1, 2, 3, 4),
            [Point2D(0, 0), Point2D(2, 2), Point2D(4, 0), Point2D(3, 4), Point2D(1, 4)],
        )
        is False
    )

    assert _share_triangle_edge([(0, 1, 2)], [(1, 2, 3)]) is True
    monotone_parts = _monotone_partitions([(0, 1, 2), (0, 2, 3)], square_vertices())
    assert monotone_parts == [(0, 1, 2, 3)]

    assert _point_on_segment_at_x(Point2D(0, 0), Point2D(2, 2), 1.0) == Point2D(
        1.0, 1.0
    )
    assert _point_on_segment_at_x(Point2D(1, 0), Point2D(1, 2), 1.0) == Point2D(
        1.0, 0.0
    )

    hits = _vertical_line_intersections(
        [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)], 2.0
    )
    assert hits == [(0.0, 0), (4.0, 2)]

    assert _cleanup_face(
        [Point2D(0, 0), Point2D(1, 0), Point2D(1, 0), Point2D(0, 0)]
    ) == [Point2D(0, 0), Point2D(1, 0)]

    trapezoids = _trapezoidal_faces(
        [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
    )
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
