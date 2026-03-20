
import math
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.algo import shapes

def test_line_segment():
    p1, p2 = Point2D(0, 0), Point2D(3, 4)
    ls = shapes.LineSegment(p1, p2)
    assert ls.length == 5.0
    assert ls.diameter == 5.0
    assert ls.centroid == Point2D(1.5, 2.0)
    assert "LineSegment" in repr(ls)

    p1_3d, p2_3d = Point3D(0, 0, 0), Point3D(0, 0, 10)
    ls_3d = shapes.LineSegment(p1_3d, p2_3d)
    assert ls_3d.length == 10.0
    assert ls_3d.centroid == Point3D(0, 0, 5)

def test_ray():
    o, d = Point2D(0, 0), Point2D(1, 1)
    ray = shapes.Ray(o, d)
    assert ray.centroid == o
    assert ray.diameter == float('inf')
    assert "Ray" in repr(ray)

def test_circle():
    c = Point2D(0, 0)
    r = 2.0
    circle = shapes.Circle(c, r)
    assert circle.radius == 2.0
    assert circle.centroid == c
    assert circle.diameter == 4.0
    assert circle.area == pytest.approx(math.pi * 4)
    assert circle.perimeter == pytest.approx(2 * math.pi * 2)
    assert "Circle" in repr(circle)

def test_rectangle_and_square():
    rect = shapes.Rectangle(Point2D(0, 0), 4, 2)
    assert rect.width == 4
    assert rect.height == 2
    assert rect.area == 8.0
    assert rect.perimeter == 12.0
    assert rect.diameter == pytest.approx(math.sqrt(20))
    assert len(rect.vertices) == 4
    
    sq = shapes.Square(Point2D(5, 5), 2)
    assert sq.side_length == 2
    assert sq.area == 4.0
    assert "Square" in repr(sq)

def test_triangle():
    a, b, c = Point2D(0, 0), Point2D(2, 0), Point2D(0, 2)
    tri = shapes.Triangle(a, b, c)
    assert tri.area == 2.0
    assert tri.perimeter == pytest.approx(4 + math.sqrt(8))
    assert tri.centroid == Point2D(2/3, 2/3)
    assert tri.diameter == pytest.approx(math.sqrt(8))

def test_plane():
    p = Point3D(0, 0, 0)
    n = (0, 0, 1)
    plane = shapes.Plane(p, n)
    assert plane.centroid == p
    assert plane.diameter == float('inf')
    assert "Plane" in repr(plane)

def test_tetrahedron():
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)
    d = Point3D(0, 0, 1)
    tetra = shapes.Tetrahedron(a, b, c, d)
    assert tetra.volume == pytest.approx(1/6)
    assert tetra.surface_area == pytest.approx(0.5 * 3 + (0.5 * math.sqrt(3)))
    assert tetra.centroid == Point3D(0.25, 0.25, 0.25)
    assert tetra.diameter == pytest.approx(math.sqrt(2))

def test_sphere():
    s = shapes.Sphere(Point3D(0, 0, 0), 1.0)
    assert s.volume == pytest.approx(4/3 * math.pi)
    assert s.surface_area == pytest.approx(4 * math.pi)
    assert s.diameter == 2.0

def test_cuboid_and_cube():
    cuboid = shapes.Cuboid(Point3D(0, 0, 0), 2, 3, 4)
    assert cuboid.volume == 24.0
    assert cuboid.surface_area == 2 * (6 + 12 + 8)
    assert cuboid.diameter == pytest.approx(math.sqrt(4 + 9 + 16))
    
    cube = shapes.Cube(Point3D(0, 0, 0), 2.0)
    assert cube.volume == 8.0
    assert cube.surface_area == 24.0
    assert cube.diameter == pytest.approx(math.sqrt(12))

def test_hexahedron():
    # A unit cube centered at (0.5, 0.5, 0.5)
    v = [
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
    ]
    hex = shapes.Hexahedron(v)
    assert hex.volume == pytest.approx(1.0)
    assert hex.surface_area == pytest.approx(6.0)
    assert hex.centroid == Point3D(0.5, 0.5, 0.5)
    
    with pytest.raises(ValueError):
        shapes.Hexahedron(v[:7])
