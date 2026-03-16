import math
import pytest

from compgeom.kernel import Point2D
from compgeom.graphics.geo_plot import GeomPlot
from compgeom.polygon.convex_hull import ConvexHull, GrahamScan, MonotoneChain, QuickHull, Chan
from compgeom.polygon.polygon_metrics import is_point_in_polygon
from compgeom.polygon import (
    Polygon,
    triangulate_polygon,
    triangulate_polygon_with_holes,
    convex_decompose_polygon,
    monotone_decompose_polygon,
    trapezoidal_decompose_polygon,
    visibility_decompose_polygon,
    decompose_polygon,
    art_gallery_guards,
    compute_visibility_polygon,
    generate_convex_polygon,
    generate_concave_polygon,
    get_convex_diameter,
    get_polygon_properties,
    get_reflex_vertices,
    is_polygon_convex,
    shortest_path_in_polygon,
)

def test_polygon_properties_class_and_wrapper():
    polygon = Polygon([Point2D(0, 0), Point2D(4, 0), Point2D(0, 2)])

    properties = polygon.properties()
    # area, centroid, orientation
    props_wrapper = get_polygon_properties(polygon.as_list())

    assert math.isclose(properties.area, 4.0, abs_tol=1e-9)
    assert properties.centroid == Point2D(4 / 3, 2 / 3)
    assert properties.orientation == "CCW"
    
    assert math.isclose(props_wrapper.area, properties.area, abs_tol=1e-9)
    assert props_wrapper.centroid == properties.centroid
    assert props_wrapper.orientation == properties.orientation

def test_polygon_contains_point_and_wrapper():
    polygon = Polygon([Point2D(0, 0), Point2D(3, 0), Point2D(3, 3), Point2D(0, 3)])

    assert polygon.contains_point(Point2D(1, 1)) is True
    assert polygon.contains_point(Point2D(0, 1)) is True
    assert polygon.contains_point(Point2D(4, 1)) is False

    assert is_point_in_polygon(Point2D(1, 1), polygon.as_list()) is True
    assert is_point_in_polygon(Point2D(4, 1), polygon.as_list()) is False

def test_polygon_triangulate():
    polygon_points = [Point2D(0, 0), Point2D(2, 0), Point2D(3, 1), Point2D(1, 3), Point2D(0, 2)]
    
    triangles, diagonals, ordered_vertices = triangulate_polygon(polygon_points, collect_diagonals=True)

    assert len(triangles) == len(polygon_points) - 2
    assert len(diagonals) == len(polygon_points) - 3

def test_visibility_polygon_for_convex_polygon_returns_same_boundary():
    polygon = Polygon([Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)])
    viewpoint = Point2D(2, 2)
    visible = compute_visibility_polygon(polygon, viewpoint)

    assert len(visible.vertices) == 4
    assert set(visible.vertices) == set(polygon.vertices)

def test_shortest_path_in_convex_polygon_is_direct_segment():
    polygon = Polygon([Point2D(0, 0), Point2D(5, 0), Point2D(5, 5), Point2D(0, 5)])
    source = Point2D(1, 1)
    target = Point2D(4, 4)

    path, path_length = shortest_path_in_polygon(polygon.as_list(), source, target)

    assert path == [source, target]
    assert math.isclose(path_length, math.sqrt(18), abs_tol=1e-9)

def test_triangulate_polygon_with_holes_returns_non_empty_result():
    outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
    hole = [Point2D(2, 2), Point2D(2, 4), Point2D(4, 4), Point2D(4, 2)]

    triangles, merged_vertices = triangulate_polygon_with_holes(outer, [hole])
    assert triangles
    assert merged_vertices

def test_art_gallery_guards():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 1), Point2D(2, 2), Point2D(4, 4), Point2D(0, 4)]
    guards = art_gallery_guards(polygon_points)
    assert len(guards) > 0

def test_geomplot_renders_polygon_with_guard_overlay():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 1), Point2D(2, 2), Point2D(4, 4), Point2D(0, 4)]
    polygon = Polygon(polygon_points)
    guards = art_gallery_guards(polygon_points)

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
    convex = Polygon([Point2D(0, 0), Point2D(4, 0), Point2D(4, 3), Point2D(0, 3)])
    concave_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
    concave = Polygon(concave_points)

    assert convex.is_convex() is True
    assert is_polygon_convex(convex.as_list()) is True
    assert concave.is_convex() is False
    assert is_polygon_convex(concave_points) is False
    assert set(get_reflex_vertices(concave_points)) == {Point2D(2, 2)}
    assert set(concave.reflex_vertices()) == {Point2D(2, 2)}
    assert math.isclose(convex.convex_diameter(), 5.0, abs_tol=1e-9)
    assert math.isclose(get_convex_diameter(convex.as_list()), 5.0, abs_tol=1e-9)

def test_polygon_random_generators():
    random_convex = generate_convex_polygon(8)
    random_concave = generate_concave_polygon(8)
    hull_points = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1), Point2D(0.2, 0.2)]

    assert len(random_convex.vertices) >= 3
    assert len(random_concave.vertices) == 8
    
    gs_hull = GrahamScan().generate(hull_points)
    assert len(gs_hull) == 3
    assert Point2D(0.2, 0.2) not in gs_hull

def test_convex_hull_algorithms_match():
    points = [
        Point2D(0, 0),
        Point2D(4, 0),
        Point2D(5, 2),
        Point2D(3, 5),
        Point2D(0, 4),
        Point2D(2, 2),
        Point2D(3, 1),
        Point2D(1, 3),
    ]

    expected = sorted(MonotoneChain().generate(points), key=lambda p: (p.x, p.y))

    assert sorted(QuickHull().generate(points), key=lambda p: (p.x, p.y)) == expected
    assert sorted(Chan().generate(points), key=lambda p: (p.x, p.y)) == expected
    assert sorted(GrahamScan().generate(points), key=lambda p: (p.x, p.y)) == expected

def test_visibility_polygon_rejects_outside_viewpoint():
    polygon = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)])
    with pytest.raises(ValueError):
        compute_visibility_polygon(polygon, Point2D(5, 5))
