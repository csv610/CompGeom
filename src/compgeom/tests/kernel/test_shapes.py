import pytest
import math
from compgeom.kernel import Point2D, Point3D
from compgeom.algo.shapes import (
    LineSegment, Ray, Circle, Rectangle, Square, Triangle,
    Plane, Tetrahedron, Sphere, Cuboid, Hexahedron, Cube
)

def test_line_segment():
    p1, p2 = Point2D(0, 0), Point2D(3, 4)
    ls = LineSegment(p1, p2)
    assert ls.length == 5.0
    assert ls.centroid == Point2D(1.5, 2.0)
    assert ls.diameter == 5.0

def test_line_segment_3d():
    p1, p2 = Point3D(0, 0, 0), Point3D(1, 1, 1)
    ls = LineSegment(p1, p2)
    assert ls.length == pytest.approx(math.sqrt(3))
    assert ls.centroid == Point3D(0.5, 0.5, 0.5)

def test_ray():
    r = Ray(Point2D(0, 0), Point2D(1, 1))
    assert r.centroid == Point2D(0, 0)
    assert r.diameter == float('inf')

def test_circle():
    c = Circle(Point2D(0, 0), 2.0)
    assert c.area == pytest.approx(math.pi * 4)
    assert c.perimeter == pytest.approx(math.pi * 4)
    assert c.diameter == 4.0

def test_rectangle():
    r = Rectangle(Point2D(0, 0), 4, 3)
    assert r.area == 12.0
    assert r.perimeter == 14.0
    assert r.diameter == 5.0
    assert len(r.vertices) == 4

def test_square():
    s = Square(Point2D(0, 0), 2.0)
    assert s.area == 4.0
    assert s.side_length == 2.0

def test_triangle_shape():
    t = Triangle(Point2D(0, 0), Point2D(1, 0), Point2D(0, 1))
    assert t.area == 0.5
    assert t.perimeter == pytest.approx(2 + math.sqrt(2))
    assert t.centroid == Point2D(1/3, 1/3)

def test_plane():
    p = Plane(Point3D(0, 0, 0), (0, 0, 1))
    assert p.centroid == Point3D(0, 0, 0)

def test_tetrahedron():
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)
    d = Point3D(0, 0, 1)
    t = Tetrahedron(a, b, c, d)
    assert t.volume == pytest.approx(1/6)
    assert t.surface_area > 0
    assert t.centroid == Point3D(0.25, 0.25, 0.25)

def test_sphere():
    s = Sphere(Point3D(0, 0, 0), 1.0)
    assert s.volume == pytest.approx(4/3 * math.pi)
    assert s.surface_area == pytest.approx(4 * math.pi)

def test_cuboid():
    c = Cuboid(Point3D(0, 0, 0), 1, 2, 3)
    assert c.volume == 6.0
    assert c.surface_area == 22.0
    assert c.diameter == pytest.approx(math.sqrt(1**2 + 2**2 + 3**2))

def test_cube():
    c = Cube(Point3D(0, 0, 0), 2.0)
    assert c.volume == 8.0
    assert c.surface_area == 24.0
    assert c.side_length == 2.0

def test_hexahedron():
    # A unit cube as hexahedron
    v = [
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1)
    ]
    h = Hexahedron(v)
    assert h.volume == pytest.approx(1.0)
    assert h.surface_area == pytest.approx(6.0)
