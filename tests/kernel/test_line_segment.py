
import math
import pytest
from compgeom.kernel.point import Point2D
from compgeom.kernel.line_segment import LineSegment
from compgeom.kernel import line_segment as seg_module

@pytest.fixture
def horiz_segment():
    return LineSegment(start=Point2D(0, 0), end=Point2D(10, 0))

@pytest.fixture
def diag_segment():
    return LineSegment(start=Point2D(1, 1), end=Point2D(4, 5))

def test_linesegment_class(horiz_segment, diag_segment):
    """Test the methods of the LineSegment class."""
    # length
    assert horiz_segment.length() == pytest.approx(10.0)
    assert diag_segment.length() == pytest.approx(5.0) # 3-4-5 triangle

    # midpoint
    assert horiz_segment.midpoint() == Point2D(5, 0)
    assert diag_segment.midpoint() == Point2D(2.5, 3.0)

    # direction
    dir_h = horiz_segment.direction()
    assert dir_h.x == pytest.approx(1.0)
    assert dir_h.y == pytest.approx(0.0)
    
    dir_d = diag_segment.direction()
    assert dir_d.x == pytest.approx(3.0 / 5.0)
    assert dir_d.y == pytest.approx(4.0 / 5.0)
    
    # distance_to_point
    assert horiz_segment.distance_to_point(Point2D(5, 3)) == pytest.approx(3.0)
    assert horiz_segment.distance_to_point(Point2D(12, 0)) == pytest.approx(2.0) # Off the end
    assert horiz_segment.distance_to_point(Point2D(-2, 0)) == pytest.approx(2.0) # Off the start

def test_intersect_lines():
    """Test the standalone intersect_lines function."""
    p1, p2 = Point2D(0, 0), Point2D(2, 2)
    p3, p4 = Point2D(0, 2), Point2D(2, 0)
    intersection = seg_module.intersect_lines(p1, p2, p3, p4)
    assert intersection == Point2D(1, 1)
    
    # Parallel lines
    p5, p6 = Point2D(0, 1), Point2D(2, 3)
    assert seg_module.intersect_lines(p1, p2, p5, p6) is None

def test_distance_to_point(horiz_segment):
    """Test the standalone distance_to_point function."""
    start, end = horiz_segment.start, horiz_segment.end
    assert seg_module.distance_to_point(Point2D(5, 3), start, end) == pytest.approx(3.0)
    assert seg_module.distance_to_point(Point2D(12, 0), start, end) == pytest.approx(2.0)

def test_contains_point(horiz_segment):
    """Test the standalone contains_point function."""
    start, end = horiz_segment.start, horiz_segment.end
    assert seg_module.contains_point(Point2D(5, 0), start, end) is True
    assert seg_module.contains_point(Point2D(11, 0), start, end) is False
    assert seg_module.contains_point(Point2D(5, 0.1), start, end) is False

def test_intersect_proper():
    """Test the standalone intersect_proper function."""
    a, b = Point2D(0, 0), Point2D(2, 2)
    c, d = Point2D(0, 2), Point2D(2, 0)
    assert seg_module.intersect_proper(a, b, c, d) is True

    # Parallel
    e, f = Point2D(0, 1), Point2D(2, 3)
    assert seg_module.intersect_proper(a, b, e, f) is False
    
    # Touching at endpoint
    g, h = Point2D(2, 2), Point2D(3, 1)
    assert seg_module.intersect_proper(a, b, g, h) is False

def test_intersect_ray():
    """Test the standalone intersect_ray function."""
    start, end = Point2D(5, 5), Point2D(10, 5)
    
    # Ray intersecting from below
    origin = Point2D(7, 0)
    angle = math.pi / 2 # Straight up
    dist, point = seg_module.intersect_ray(origin, angle, start, end)
    assert dist == pytest.approx(5.0)
    assert point == Point2D(7, 5)
    
    # Ray missing
    angle_miss = math.pi / 4
    assert seg_module.intersect_ray(origin, angle_miss, start, end) is None

def test_midpoint_and_angle():
    """Test midpoint and angle helper functions."""
    p1, p2 = Point2D(1, 1), Point2D(2, 2)
    assert seg_module.midpoint(p1, p2) == Point2D(1.5, 1.5)
    assert seg_module.angle(p1, p2) == pytest.approx(math.pi / 4)
