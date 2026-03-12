import pytest
import math
from compgeom.kernel import Point
from compgeom.algo.bounding import minimum_bounding_box, minimum_enclosing_circle

def test_minimum_enclosing_circle():
    points = [Point(0, 0), Point(1, 0), Point(0, 1)]
    center, radius = minimum_enclosing_circle(points)
    assert center == Point(0.5, 0.5)
    assert radius == pytest.approx(math.sqrt(0.5**2 + 0.5**2))

def test_minimum_enclosing_circle_empty():
    center, radius = minimum_enclosing_circle([])
    assert center == Point(0, 0)
    assert radius == 0.0

def test_minimum_bounding_box():
    # A square rotated by 45 degrees
    points = [Point(1, 0), Point(0, 1), Point(-1, 0), Point(0, -1)]
    bbox = minimum_bounding_box(points)
    assert bbox["area"] == pytest.approx(2.0)
    assert bbox["width"] == pytest.approx(math.sqrt(2.0))
    assert bbox["height"] == pytest.approx(math.sqrt(2.0))

def test_minimum_bounding_box_empty():
    bbox = minimum_bounding_box([])
    assert bbox["area"] == 0.0
    assert len(bbox["corners"]) == 0

def test_minimum_bounding_box_single_point():
    p = Point(1, 2)
    bbox = minimum_bounding_box([p])
    assert bbox["area"] == 0.0
    assert bbox["center"] == p

def test_minimum_bounding_box_two_points():
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    bbox = minimum_bounding_box([p1, p2])
    assert bbox["width"] == pytest.approx(math.sqrt(2.0))
    assert bbox["height"] == 0.0
