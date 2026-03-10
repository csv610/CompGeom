import math

import pytest

from compgeom.geo_math.geometry import Point
from compgeom.graphics.geo_plot import GeomPlot
from compgeom.polygon import (
    ConvexHull,
    Polygon,
    PolygonGuards,
    PolygonGenerator,
    PolygonProperties,
    generate_random_convex_polygon,
    generate_simple_polygon,
    get_convex_diameter,
    get_polygon_properties,
    get_reflex_vertices,
    get_triangulation_with_diagonals,
    hertel_mehlhorn,
    is_convex,
    is_point_in_polygon,
    shortest_path_in_polygon,
    polygon_kernel,
    solve_art_gallery,
    triangulate_polygon,
    triangulate_polygon_with_holes,
    visibility_polygon,
)


def test_polygon_properties_class_and_wrapper():
    polygon = Polygon([Point(0, 0), Point(4, 0), Point(0, 2)])

    properties = polygon.properties()
    area, centroid, orientation = get_polygon_properties(polygon.as_list())

    assert isinstance(properties, PolygonProperties)
    assert math.isclose(properties.area, 4.0, abs_tol=1e-9)
    assert properties.centroid == Point(4 / 3, 2 / 3)
    assert properties.orientation == "CCW"
    assert math.isclose(area, properties.area, abs_tol=1e-9)
    assert centroid == properties.centroid
    assert orientation == properties.orientation


def test_polygon_contains_point_and_wrapper():
    polygon = Polygon([Point(0, 0), Point(3, 0), Point(3, 3), Point(0, 3)])

    assert polygon.contains_point(Point(1, 1)) is True
    assert polygon.contains_point(Point(0, 1)) is True
    assert polygon.contains_point(Point(4, 1)) is False

    assert is_point_in_polygon(Point(1, 1), polygon.as_list()) is True
    assert is_point_in_polygon(Point(4, 1), polygon.as_list()) is False


def test_polygon_triangulate_and_diagonals():
    polygon = Polygon([Point(0, 0), Point(2, 0), Point(3, 1), Point(1, 3), Point(0, 2)])

    triangles, ordered_vertices = polygon.triangulate()
    triangles2, diagonals, ordered_vertices2 = polygon.triangulation_with_diagonals()

    assert len(triangles) == len(polygon) - 2
    assert len(triangles2) == len(polygon) - 2
    assert len(diagonals) == len(polygon) - 3
    assert ordered_vertices == ordered_vertices2
    assert triangulate_polygon(polygon.as_list()) == (triangles, ordered_vertices)
    assert get_triangulation_with_diagonals(polygon.as_list()) == (triangles2, diagonals, ordered_vertices2)


def test_visibility_polygon_for_convex_polygon_returns_same_boundary():
    polygon = Polygon([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])

    visible = polygon.visibility_polygon(Point(2, 2))

    assert len(visible) == 4
    assert set(visible) == set(polygon.as_list())
    assert set(visibility_polygon(Point(2, 2), polygon.as_list())) == set(polygon.as_list())


def test_polygon_kernel_for_convex_polygon_returns_same_boundary():
    polygon = Polygon([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])

    kernel = polygon.kernel()

    assert len(kernel) == 4
    assert set(kernel) == set(polygon.as_list())
    assert set(polygon_kernel(polygon.as_list())) == set(polygon.as_list())


def test_polygon_kernel_for_concave_polygon_returns_smaller_region():
    polygon_points = [Point(0, 0), Point(4, 0), Point(4, 4), Point(2, 2), Point(0, 4)]
    polygon = Polygon(polygon_points)

    kernel = polygon.kernel()

    assert kernel
    assert len(kernel) == 3
    assert set(kernel) == {Point(0, 0), Point(4, 0), Point(2, 2)}
    assert set(polygon_kernel(polygon_points)) == set(kernel)


def test_shortest_path_in_convex_polygon_is_direct_segment():
    polygon = Polygon([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
    source = Point(1, 1)
    target = Point(4, 4)

    path, path_length = polygon.shortest_path(source, target)
    wrapper_path, wrapper_length = shortest_path_in_polygon(polygon.as_list(), source, target)

    assert path == [source, target]
    assert math.isclose(path_length, math.sqrt(18), abs_tol=1e-9)
    assert wrapper_path == path
    assert math.isclose(wrapper_length, path_length, abs_tol=1e-9)


def test_triangulate_polygon_with_holes_returns_non_empty_result():
    outer = [Point(0, 0), Point(6, 0), Point(6, 6), Point(0, 6)]
    hole = [Point(2, 2), Point(2, 4), Point(4, 4), Point(4, 2)]

    triangles, merged = Polygon(outer).triangulate_with_holes([hole])
    wrapper_triangles, wrapper_merged = triangulate_polygon_with_holes(outer, [hole])

    assert triangles
    assert merged
    assert wrapper_triangles == triangles
    assert wrapper_merged == merged


def test_art_gallery_and_hertel_mehlhorn_return_expected_shapes():
    polygon_points = [Point(0, 0), Point(4, 0), Point(4, 1), Point(2, 2), Point(4, 4), Point(0, 4)]
    polygon = Polygon(polygon_points)

    guards = PolygonGuards.solve_art_gallery(polygon_points)
    wrapper_guards = solve_art_gallery(polygon_points)
    partitions, ordered = polygon.hertel_mehlhorn()
    wrapper_partitions, wrapper_ordered = hertel_mehlhorn(polygon_points)

    assert guards
    assert wrapper_guards == guards
    assert partitions
    assert ordered == wrapper_ordered
    assert wrapper_partitions == partitions


def test_polygon_guards_class_matches_functional_api():
    polygon_points = [Point(0, 0), Point(4, 0), Point(4, 1), Point(2, 2), Point(4, 4), Point(0, 4)]
    triangles, vertices = triangulate_polygon(polygon_points)

    class_guards = PolygonGuards.solve_art_gallery(polygon_points)
    class_direct_guards = PolygonGuards.guard_polygon(triangles, vertices)
    wrapper_guards = solve_art_gallery(polygon_points)

    assert class_guards == wrapper_guards
    assert class_direct_guards == wrapper_guards


def test_geomplot_renders_polygon_with_guard_overlay():
    polygon_points = [Point(0, 0), Point(4, 0), Point(4, 1), Point(2, 2), Point(4, 4), Point(0, 4)]
    polygon = Polygon(polygon_points)
    guards = PolygonGuards.solve_art_gallery(polygon_points)

    svg = GeomPlot.get_image(
        [polygon, guards],
        format="svg",
        edge_color="blue",
        color="red",
        size=8,
    )

    assert "<svg" in svg
    assert svg.count("<polygon") >= 1
    assert svg.count("<circle") == len(guards)


def test_polygon_convexity_reflex_vertices_and_diameter():
    convex = Polygon([Point(0, 0), Point(4, 0), Point(4, 3), Point(0, 3)])
    concave_points = [Point(0, 0), Point(4, 0), Point(4, 4), Point(2, 2), Point(0, 4)]
    concave = Polygon(concave_points)

    assert convex.is_convex() is True
    assert is_convex(convex.as_list()) is True
    assert concave.is_convex() is False
    assert is_convex(concave_points) is False
    assert get_reflex_vertices(concave_points) == [Point(2, 2)]
    assert concave.reflex_vertices() == [Point(2, 2)]
    assert math.isclose(convex.convex_diameter(), 5.0, abs_tol=1e-9)
    assert math.isclose(get_convex_diameter(convex.as_list()), 5.0, abs_tol=1e-9)


def test_polygon_random_generators_return_polygon_compatible_shapes():
    random_convex = Polygon.from_random_convex(8)
    random_simple = Polygon.from_simple_random(8)
    hull_points = [Point(0, 0), Point(1, 0), Point(0, 1), Point(0.2, 0.2)]

    assert len(random_convex) >= 3
    assert len(random_simple) == 8
    assert ConvexHull.graham_scan(hull_points) == [Point(0, 0), Point(1, 0), Point(0, 1)]
    assert ConvexHull.monotone_chain(hull_points) == [Point(0, 0), Point(1, 0), Point(0, 1)]
    assert len(PolygonGenerator.convex(8)) >= 3
    assert len(generate_random_convex_polygon(8)) >= 3
    assert len(generate_simple_polygon(8)) == 8


def test_convex_hull_quick_hull_matches_other_hull_algorithms():
    points = [
        Point(0, 0),
        Point(4, 0),
        Point(5, 2),
        Point(3, 5),
        Point(0, 4),
        Point(2, 2),
        Point(3, 1),
        Point(1, 3),
    ]

    expected = ConvexHull.monotone_chain(points)

    assert ConvexHull.quick_hull(points) == expected
    assert ConvexHull.chan(points) == expected
    assert ConvexHull.graham_scan(points) == expected
    assert ConvexHull.is_convex_hull(points, expected) is True
    assert ConvexHull.is_convex_hull(points, [Point(0, 0), Point(4, 0), Point(2, 2), Point(0, 4)]) is False


def test_visibility_polygon_rejects_outside_viewpoint():
    polygon = Polygon([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)])

    with pytest.raises(ValueError):
        polygon.visibility_polygon(Point(5, 5))
