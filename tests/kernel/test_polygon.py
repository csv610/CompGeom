
import pytest
from compgeom.kernel.point import Point2D
from compgeom.kernel.polygon import Polygon2D

@pytest.fixture
def ccw_square():
    """A 1x1 square with counter-clockwise vertices."""
    return Polygon2D(vertices=(
        Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
    ))

@pytest.fixture
def cw_square():
    """A 1x1 square with clockwise vertices."""
    return Polygon2D(vertices=(
        Point2D(0, 0), Point2D(0, 1), Point2D(1, 1), Point2D(1, 0)
    ))

@pytest.fixture
def concave_polygon():
    """A simple concave polygon (arrowhead shape)."""
    return Polygon2D(vertices=(
        Point2D(0, 0), Point2D(2, 0), Point2D(1, 1), Point2D(2, 2), Point2D(0, 2)
    ))

def test_post_init_fails():
    """Test that polygons with < 3 vertices raise an error."""
    with pytest.raises(ValueError):
        Polygon2D(vertices=(Point2D(0, 0), Point2D(1, 1)))
    with pytest.raises(ValueError):
        Polygon2D(vertices=(Point2D(0, 0),))

def test_num_vertices(ccw_square, concave_polygon):
    assert ccw_square.num_vertices == 4
    assert concave_polygon.num_vertices == 5

def test_area(ccw_square, cw_square, concave_polygon):
    assert ccw_square.area() == pytest.approx(1.0)
    assert cw_square.area() == pytest.approx(1.0)
    assert concave_polygon.area() == pytest.approx(3.0)

def test_signed_area(ccw_square, cw_square):
    assert ccw_square.signed_area() == pytest.approx(1.0)
    assert cw_square.signed_area() == pytest.approx(-1.0)

def test_centroid(ccw_square):
    assert ccw_square.centroid() == Point2D(0.5, 0.5)
    
    triangle = Polygon2D(vertices=(Point2D(0,0), Point2D(3,0), Point2D(0,3)))
    assert triangle.centroid() == Point2D(1, 1)

def test_is_ccw(ccw_square, cw_square):
    assert ccw_square.is_ccw() is True
    assert cw_square.is_ccw() is False

def test_is_convex(ccw_square, concave_polygon):
    assert ccw_square.is_convex() is True
    assert concave_polygon.is_convex() is False
    
    collinear = Polygon2D(vertices=(Point2D(0,0), Point2D(1,0), Point2D(2,0)))
    assert collinear.is_convex() is True

def test_contains_point(ccw_square, concave_polygon):
    # Test simple cases for square
    assert ccw_square.contains_point(Point2D(0.5, 0.5)) is True
    assert ccw_square.contains_point(Point2D(1.5, 0.5)) is False
    
    # The new implementation is boundary-inclusive.
    assert ccw_square.contains_point(Point2D(0.5, 1.0)) is True
    assert ccw_square.contains_point(Point2D(1.0, 0.5)) is True
    assert ccw_square.contains_point(Point2D(1, 1)) is True

    # Test concave polygon
    assert concave_polygon.contains_point(Point2D(1.5, 1.5)) is True
    # Test point in the "dent" - should be outside
    assert concave_polygon.contains_point(Point2D(1.5, 1.1)) is False

def test_repr(ccw_square):
    assert repr(ccw_square) == "Polygon2D(n=4)"
