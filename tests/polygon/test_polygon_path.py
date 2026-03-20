import pytest
from compgeom.kernel import Point2D, distance
from compgeom.polygon import Polygon, shortest_path_in_polygon
from compgeom.polygon.polygon_path import segment_inside_polygon
from compgeom.polygon.exceptions import PointOutsidePolygonError

def test_segment_inside_polygon_accepts_visible_segment_and_rejects_crossing_segment():
    polygon = [
        Point2D(0, 0),
        Point2D(4, 0),
        Point2D(4, 1),
        Point2D(1, 1),
        Point2D(1, 4),
        Point2D(0, 4),
    ]

    assert segment_inside_polygon(polygon, Point2D(0.5, 0.5), Point2D(0.5, 3.5)) is True
    assert segment_inside_polygon(polygon, Point2D(3.5, 0.5), Point2D(0.5, 3.5)) is False

def test_shortest_path_in_concave_polygon_routes_through_reflex_vertex():
    polygon = [
        Point2D(0, 0),
        Point2D(5, 0),
        Point2D(5, 1),
        Point2D(1, 1),
        Point2D(1, 5),
        Point2D(0, 5),
    ]
    source = Point2D(4.5, 0.5)
    target = Point2D(0.5, 4.5)

    path, path_length = shortest_path_in_polygon(polygon, source, target)

    assert path[0] == source
    assert path[-1] == target
    assert Point2D(1, 1) in path
    assert path_length > distance(source, target)

def test_shortest_path_in_polygon_rejects_points_outside_boundary():
    polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]

    with pytest.raises(PointOutsidePolygonError, match="Source point must lie inside or on the boundary"):
        shortest_path_in_polygon(polygon, Point2D(-1, 1), Point2D(1, 1))

    with pytest.raises(PointOutsidePolygonError, match="Target point must lie inside or on the boundary"):
        shortest_path_in_polygon(polygon, Point2D(1, 1), Point2D(5, 1))
