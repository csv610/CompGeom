import pytest
import math
from compgeom.kernel import Point
from compgeom.algo.proximity import (
    ClosestPair, 
    LargestEmptyCircle, 
    closest_pair, 
    do_intersect, 
    farthest_pair, 
    welzl, 
    minkowski_sum
)

def test_closest_pair():
    points = [Point(0, 0), Point(1, 1), Point(0.1, 0.1), Point(10, 10)]
    d, (p1, p2) = closest_pair(points)
    assert d == pytest.approx(math.sqrt(0.1**2 + 0.1**2))
    assert (p1 == Point(0, 0) and p2 == Point(0.1, 0.1)) or (p2 == Point(0, 0) and p1 == Point(0.1, 0.1))

def test_closest_pair_empty():
    d, (p1, p2) = closest_pair([])
    assert d == float("inf")
    assert p1 is None and p2 is None

def test_grid_based_massive():
    points = [Point(x, y) for x in range(10) for y in range(10)]
    points.append(Point(0.1, 0.1))
    d, (p1, p2) = ClosestPair.grid_based_massive(iter(points), sample_size=10)
    assert d == pytest.approx(math.sqrt(0.1**2 + 0.1**2))

def test_largest_empty_circle():
    points = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10), Point(5, 5)]
    center, radius = LargestEmptyCircle.find(points)
    assert center is not None
    assert radius > 0

def test_do_intersect():
    p1, q1 = Point(0, 0), Point(10, 10)
    p2, q2 = Point(0, 10), Point(10, 0)
    assert do_intersect(p1, q1, p2, q2) is True
    
    p3, q3 = Point(0, 0), Point(1, 1)
    p4, q4 = Point(2, 2), Point(3, 3)
    assert do_intersect(p3, q3, p4, q4) is False

def test_farthest_pair():
    points = [Point(0, 0), Point(1, 1), Point(10, 0), Point(0, 10)]
    d, (p1, p2) = farthest_pair(points)
    assert d == pytest.approx(math.sqrt(10**2 + 10**2))
    assert (p1 == Point(10, 0) and p2 == Point(0, 10)) or (p2 == Point(10, 0) and p1 == Point(0, 10))

def test_welzl():
    points = [Point(0, 0), Point(1, 0), Point(0, 1)]
    # For a right triangle, the smallest enclosing circle is the circumcircle if it's not obtuse.
    # For (0,0), (1,0), (0,1), it's the circle with diameter (1,0)-(0,1).
    center, radius = welzl(points, [])
    assert center == Point(0.5, 0.5)
    assert radius == pytest.approx(math.sqrt(0.5**2 + 0.5**2))

def test_minkowski_sum():
    poly1 = [Point(0, 0), Point(1, 0), Point(0, 1)]
    poly2 = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    result = minkowski_sum(poly1, poly2)
    assert len(result) > 0
    # Minkowski sum of a triangle and a square should be a convex polygon.
    # (0,0)+(0,0)=(0,0)
    # (1,0)+(1,1)=(2,1) etc.
    assert Point(0, 0) in result
    assert Point(2, 1) in result
