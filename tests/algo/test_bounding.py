
import math
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.algo import bounding

def test_largest_empty_circle():
    points = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(5, 5)]
    center, radius = bounding.largest_empty_circle(points)
    assert center is not None
    assert radius > 0

def test_minimum_enclosing_circle():
    points = [Point2D(0, 0), Point2D(2, 0), Point2D(1, 1)]
    center, radius = bounding.minimum_enclosing_circle(points)
    assert center == Point2D(1, 0)
    assert radius == pytest.approx(1.0)

def test_minimum_bounding_box_empty():
    res = bounding.minimum_bounding_box([])
    assert res["area"] == 0.0
    assert res["corners"] == []

def test_minimum_bounding_box_single_point():
    p = Point2D(1, 2)
    res = bounding.minimum_bounding_box([p])
    assert res["area"] == 0.0
    assert res["center"] == p
    assert len(res["corners"]) == 4

def test_minimum_bounding_box_two_points():
    p1 = Point2D(0, 0)
    p2 = Point2D(10, 0)
    res = bounding.minimum_bounding_box([p1, p2])
    assert res["area"] == 0.0
    assert res["width"] == 10.0
    assert res["height"] == 0.0
    assert res["center"] == Point2D(5, 0)

def test_minimum_bounding_box_square():
    points = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    res = bounding.minimum_bounding_box(points)
    assert res["area"] == pytest.approx(1.0)
    assert res["width"] == pytest.approx(1.0)
    assert res["height"] == pytest.approx(1.0)

def test_minimum_bounding_box_rotated():
    # Points forming a square rotated by 45 degrees
    s = math.sqrt(2) / 2
    points = [Point2D(1, 0), Point2D(0, 1), Point2D(-1, 0), Point2D(0, -1)]
    res = bounding.minimum_bounding_box(points)
    assert res["area"] == pytest.approx(2.0)
    assert res["width"] == pytest.approx(math.sqrt(2))
    assert res["height"] == pytest.approx(math.sqrt(2))

def test_largest_empty_sphere():
    points = [Point3D(x, y, z) for x in [0, 10] for y in [0, 10] for z in [0, 10]]
    points.append(Point3D(5, 5, 5))
    center, radius = bounding.largest_empty_sphere(points)
    assert center is not None
    assert radius > 0

def test_largest_empty_oriented_shapes():
    points_3d = [Point3D(x, y, z) for x in [0, 10] for y in [0, 10] for z in [0, 10]]
    points_2d = [Point2D(x, y) for x in [0, 10] for y in [0, 10]]
    
    assert "volume" in bounding.largest_empty_oriented_box(points_3d)
    assert "volume" in bounding.largest_empty_oriented_ellipsoid(points_3d)
    assert "area" in bounding.largest_empty_oriented_rectangle(points_2d)
    assert "area" in bounding.largest_empty_oriented_ellipse(points_2d)
