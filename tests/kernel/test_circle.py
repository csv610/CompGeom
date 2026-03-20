
import math
import pytest
from compgeom.kernel.point import Point2D
from compgeom.kernel.line_segment import LineSegment
from compgeom.kernel import circle as circle_module
from compgeom.kernel.circle import Circle2D, incircle_sign, in_circle, robust_in_circle

@pytest.fixture
def unit_circle():
    return Circle2D(center=Point2D(0, 0), radius=1.0)

def test_circle_methods(unit_circle):
    """Test the methods of the Circle2D class."""
    assert unit_circle.area() == pytest.approx(math.pi)
    assert unit_circle.perimeter() == pytest.approx(2 * math.pi)
    assert unit_circle.contains_point(Point2D(0.5, 0.5)) is True
    assert unit_circle.contains_point(Point2D(1, 0)) is True # on boundary
    assert unit_circle.contains_point(Point2D(1, 1)) is False

def test_standalone_area_perimeter():
    """Test the standalone area and perimeter functions."""
    assert circle_module.area(1.0) == pytest.approx(math.pi)
    assert circle_module.perimeter(1.0) == pytest.approx(2 * math.pi)

def test_from_two_points():
    """Test circle creation from two points."""
    center, radius = circle_module.from_two_points(Point2D(-2, 0), Point2D(2, 0))
    assert center == Point2D(0, 0)
    assert radius == pytest.approx(2.0)

def test_from_three_points():
    """Test circle creation from three points."""
    # Right-angled triangle
    p1, p2, p3 = Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)
    center, radius = circle_module.from_three_points(p1, p2, p3)
    assert center == Point2D(1, 1)
    assert radius == pytest.approx(math.sqrt(2))
    
    # Collinear points fallback
    p1c, p2c, p3c = Point2D(0, 0), Point2D(1, 0), Point2D(3, 0)
    center, radius = circle_module.from_three_points(p1c, p2c, p3c)
    assert center == Point2D(1.5, 0)
    assert radius == pytest.approx(1.5)

def test_incircle_predicates():
    """Test the suite of incircle predicates."""
    a, b, c = Point2D(0, 1), Point2D(-1, 0), Point2D(1, 0) # CCW unit circle
    d_in = Point2D(0, 0)
    d_out = Point2D(2, 2)
    d_on = Point2D(0, -1)
    
    # Test incircle_sign
    assert incircle_sign(a, b, c, d_in) == 1
    assert incircle_sign(a, b, c, d_out) == -1
    assert incircle_sign(a, b, c, d_on) == 0
    
    # Test in_circle
    assert in_circle(a, b, c, d_in) is True
    assert in_circle(a, b, c, d_out) is False
    assert in_circle(a, b, c, d_on) is False

def test_robust_in_circle():
    """Test the robust_in_circle predicate."""
    a, b, c = Point2D(0, 1, id=0), Point2D(-1, 0, id=1), Point2D(1, 0, id=2)
    d_in = Point2D(0, 0, id=3)
    d_out = Point2D(10, 10, id=4) # Far away to test bounding box
    d_on = Point2D(0, -1, id=5)

    assert robust_in_circle(a, b, c, d_in) is True
    assert robust_in_circle(a, b, c, d_out) is False
    # Test the SOS tie-breaker
    # max_id is 5 (d_on), so d.id != max_id is false
    assert robust_in_circle(a, b, c, d_on) is False

def test_tangents_from_point(unit_circle):
    """Test tangent creation from a point."""
    # Point outside
    p_out = Point2D(2, 0)
    tangents = circle_module.tangents_from_point(unit_circle, p_out)
    assert len(tangents) == 2
    assert tangents[0].start == p_out
    # Check tangent point property: distance from center is radius
    assert abs(circle_module.distance(unit_circle.center, tangents[0].end) - unit_circle.radius) < 1e-9

    # Point on circle
    p_on = Point2D(1, 0)
    tangents_on = circle_module.tangents_from_point(unit_circle, p_on)
    assert len(tangents_on) == 1
    assert tangents_on[0] == LineSegment(p_on, p_on)
    
    # Point inside
    p_in = Point2D(0.5, 0)
    assert circle_module.tangents_from_point(unit_circle, p_in) == []

def test_common_tangents():
    """Test common tangents between two circles."""
    c1 = Circle2D(Point2D(0, 0), 1)
    
    # Non-intersecting
    c2_far = Circle2D(Point2D(3, 0), 1)
    assert len(circle_module.common_tangents(c1, c2_far)) == 4
    
    # Touching externally
    c2_touch = Circle2D(Point2D(2, 0), 1)
    assert len(circle_module.common_tangents(c1, c2_touch)) == 3
    
    # Intersecting
    c2_intersect = Circle2D(Point2D(1.5, 0), 1)
    assert len(circle_module.common_tangents(c1, c2_intersect)) == 2
    
    # One inside another
    c2_inside = Circle2D(Point2D(0.5, 0), 0.2)
    assert len(circle_module.common_tangents(c1, c2_inside)) == 0
    
    # Concentric
    c2_concentric = Circle2D(Point2D(0, 0), 2)
    assert len(circle_module.common_tangents(c1, c2_concentric)) == 0
