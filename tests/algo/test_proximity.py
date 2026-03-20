
import math
import pytest
import numpy as np
from compgeom.kernel import Point2D, Point3D
from compgeom.algo import proximity

def test_closest_pair_simple():
    points = [Point2D(0, 0), Point2D(1, 1), Point2D(0.1, 0.1)]
    dist, pair = proximity.closest_pair(points)
    assert dist == pytest.approx(math.sqrt(0.1**2 + 0.1**2))
    assert (pair[0] == Point2D(0, 0) and pair[1] == Point2D(0.1, 0.1)) or \
           (pair[1] == Point2D(0, 0) and pair[0] == Point2D(0.1, 0.1))

def test_closest_pair_empty():
    dist, pair = proximity.closest_pair([])
    assert dist == float("inf")
    assert pair == (None, None)

def test_closest_pair_divide_and_conquer():
    points = [Point2D(x, x) for x in range(10)]
    points.append(Point2D(5.1, 5.1))
    dist, pair = proximity.ClosestPair.divide_and_conquer(points)
    assert dist == pytest.approx(math.sqrt(0.1**2 + 0.1**2))

def test_closest_pair_grid_based():
    points = [Point2D(x, y) for x in range(5) for y in range(5)]
    points.append(Point2D(0.1, 0.1))
    dist, pair = proximity.ClosestPair.grid_based_massive(iter(points), sample_size=10)
    assert dist == pytest.approx(math.sqrt(0.1**2 + 0.1**2))

def test_do_intersect():
    p1, q1 = Point2D(0, 0), Point2D(2, 2)
    p2, q2 = Point2D(0, 2), Point2D(2, 0)
    assert proximity.do_intersect(p1, q1, p2, q2) is True
    
    p3, q3 = Point2D(0, 0), Point2D(1, 0)
    p4, q4 = Point2D(2, 0), Point2D(3, 0)
    assert proximity.do_intersect(p3, q3, p4, q4) is False

def test_farthest_pair():
    points = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1), Point2D(0.5, 0.5)]
    dist, pair = proximity.farthest_pair(points)
    assert dist == pytest.approx(math.sqrt(2.0))
    assert set(pair) == {Point2D(1, 0), Point2D(0, 1)}

def test_farthest_pair_degenerate():
    assert proximity.farthest_pair([]) == (0, (None, None))
    assert proximity.farthest_pair([Point2D(1,1)]) == (0, (Point2D(1,1), Point2D(1,1)))
    p1, p2 = Point2D(0,0), Point2D(1,1)
    d, pair = proximity.farthest_pair([p1, p2])
    assert d == pytest.approx(math.sqrt(2))
    assert set(pair) == {p1, p2}

def test_welzl_simple():
    points = [Point2D(0, 0), Point2D(2, 0), Point2D(1, 1)]
    center, radius = proximity.welzl(points, [])
    assert center == Point2D(1, 0)
    assert radius == pytest.approx(1.0)

def test_minkowski_sum():
    poly1 = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]
    poly2 = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]
    result = proximity.minkowski_sum(poly1, poly2)
    assert len(result) == 3
    pts = {(p.x, p.y) for p in result}
    assert (0, 0) in pts
    assert (2, 0) in pts
    assert (0, 2) in pts

def test_largest_empty_circle():
    points = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(5, 5)]
    center, radius = proximity.LargestEmptyCircle.find(points)
    assert center is not None
    assert radius > 0
    for p in points:
        assert proximity.distance(center, p) >= radius - 1e-9

def test_largest_empty_sphere():
    points = [
        Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0),
        Point3D(0, 0, 10), Point3D(10, 0, 10), Point3D(10, 10, 10), Point3D(0, 10, 10),
        Point3D(5, 5, 5)
    ]
    center, radius = proximity.LargestEmptySphere.find(points)
    assert center is not None
    assert radius > 0
    from compgeom.kernel import distance_3d
    for p in points:
        assert distance_3d(center, p) >= radius - 1e-9

def test_largest_empty_oriented_box():
    points = [
        Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0),
        Point3D(0, 0, 10), Point3D(10, 0, 10), Point3D(10, 10, 10), Point3D(0, 10, 10),
        Point3D(5, 5, 5)
    ]
    result = proximity.LargestEmptyOrientedBox.find(points)
    assert "volume" in result
    assert result["volume"] >= 0

def test_largest_empty_oriented_ellipsoid():
    points = [
        Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0),
        Point3D(0, 0, 10), Point3D(10, 0, 10), Point3D(10, 10, 10), Point3D(0, 10, 10),
        Point3D(5, 5, 5)
    ]
    result = proximity.LargestEmptyOrientedEllipsoid.find(points)
    assert "volume" in result
    assert result["volume"] >= 0

def test_largest_empty_oriented_rectangle():
    points = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(5, 5)]
    result = proximity.LargestEmptyOrientedRectangle.find(points)
    assert "area" in result
    assert result["area"] >= 0

def test_largest_empty_oriented_ellipse():
    points = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(5, 5)]
    result = proximity.LargestEmptyOrientedEllipse.find(points)
    assert "area" in result
    assert result["area"] >= 0
