import pytest
import math
from compgeom.kernel import (
    Point, Point3D, triangle_circumcenter, intersect_lines, clip_polygon,
    dist_point_to_segment, is_on_segment, contains_point,
    proper_segment_intersection, ray_segment_intersection
)

class Triangle:
    def __init__(self, a, b, c):
        self.vertices = [a, b, c]

def test_point_equality():
    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)
    p3 = Point(1.0 + 1e-10, 2.0)
    assert p1 == p2
    assert p1 == p3
    assert p1 != Point(2.0, 2.0)
    assert hash(p1) == hash(p2)

def test_point3d_equality():
    p1 = Point3D(1.0, 2.0, 3.0)
    p2 = Point3D(1.0, 2.0, 3.0)
    p3 = Point3D(1.0 + 1e-10, 2.0, 3.0)
    assert p1 == p2
    assert p1 == p3
    assert p1 != Point3D(2.0, 2.0, 3.0)

def test_get_circumcenter():
    a = Point(-1, 0)
    b = Point(1, 0)
    c = Point(0, 1)
    center = triangle_circumcenter(a, b, c)
    assert math.isclose(center.x, 0, abs_tol=1e-9)
    assert math.isclose(center.y, 0, abs_tol=1e-9)
    
    # Collinear points
    assert triangle_circumcenter(Point(0,0), Point(1,0), Point(2,0)) is None

def test_intersect_lines():
    p1 = Point(0, 0)
    p2 = Point(2, 2)
    p3 = Point(0, 2)
    p4 = Point(2, 0)
    intersect = intersect_lines(p1, p2, p3, p4)
    assert intersect.x == 1.0 and intersect.y == 1.0
    
    # Parallel
    assert intersect_lines(Point(0,0), Point(1,0), Point(0,1), Point(1,1)) is None

def test_clip_polygon():
    polygon = [Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]
    # Clip against x=1
    line_start = Point(1, 0)
    line_end = Point(1, 1)
    clipped = clip_polygon(polygon, line_start, line_end)
    assert len(clipped) == 4
    for p in clipped:
        assert p.x <= 1.0 + 1e-9

def test_dist_point_to_segment():
    start = Point(0, 0)
    end = Point(2, 0)
    assert dist_point_to_segment(Point(1, 1), start, end) == 1.0
    assert dist_point_to_segment(Point(-1, 0), start, end) == 1.0
    assert dist_point_to_segment(Point(3, 0), start, end) == 1.0

def test_is_on_segment():
    start = Point(0, 0)
    end = Point(2, 0)
    assert is_on_segment(Point(1, 0), start, end) == True
    assert is_on_segment(Point(3, 0), start, end) == False
    assert is_on_segment(Point(1, 1), start, end) == False

def test_proper_segment_intersection():
    a, b = Point(0, 0), Point(2, 2)
    c, d = Point(0, 2), Point(2, 0)
    assert proper_segment_intersection(a, b, c, d) is True
    
    # Intersection at endpoint
    assert proper_segment_intersection(a, b, b, Point(3, 3)) is False

def test_ray_segment_intersection():
    origin = Point(0, 1)
    angle = 0 # Ray pointing right
    start, end = Point(2, 0), Point(2, 2)
    t, hit = ray_segment_intersection(origin, angle, start, end)
    assert math.isclose(t, 2.0)
    assert hit == Point(2, 1)

def test_contains_point():
    t = Triangle(Point(0, 0), Point(2, 0), Point(0, 2))
    assert contains_point(t, Point(0.5, 0.5)) == True
    assert contains_point(t, Point(3, 3)) == False
    assert contains_point(t, Point(1, 1)) == True
