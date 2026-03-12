from compgeom.kernel import Point
from compgeom.polygon import is_point_in_polygon
from compgeom.polygon.polygon import Polygon

def test_point_in_polygon_inside():
    polygon = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
    assert is_point_in_polygon(Point(5, 5), polygon) is True
    assert Polygon(polygon).contains_point(Point(5, 5)) is True

def test_point_in_polygon_outside():
    polygon = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
    assert is_point_in_polygon(Point(15, 5), polygon) is False
    assert Polygon(polygon).contains_point(Point(15, 5)) is False

def test_point_in_polygon_on_edge():
    polygon = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
    assert is_point_in_polygon(Point(5, 0), polygon) is True
    assert Polygon(polygon).contains_point(Point(5, 0)) is True

def test_point_in_polygon_on_vertex():
    polygon = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
    assert is_point_in_polygon(Point(10, 10), polygon) is True
    assert Polygon(polygon).contains_point(Point(10, 10)) is True

def test_point_in_polygon_ray_crosses_vertex():
    # Polygon with a vertex that could cause issues with ray casting
    # If the ray is y=5, it hits the vertex (10, 5)
    polygon = [Point(0, 0), Point(10, 5), Point(0, 10)]
    # Point inside:
    assert is_point_in_polygon(Point(2, 5), polygon) is True
    # Point outside:
    assert is_point_in_polygon(Point(15, 5), polygon) is False

def test_point_in_polygon_collinear_edges():
    polygon = [Point(0, 0), Point(10, 0), Point(10, 5), Point(10, 10), Point(0, 10)]
    assert is_point_in_polygon(Point(10, 7), polygon) is True

def test_point_in_polygon_degenerate():
    polygon = [Point(0, 0), Point(10, 0)]
    assert is_point_in_polygon(Point(5, 5), polygon) is False
    assert is_point_in_polygon(Point(5, 0), polygon) is False # depends on implementation, usually returns False for n < 3
