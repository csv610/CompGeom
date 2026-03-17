import pytest
import math
from compgeom.kernel import Point2D, Point3D
from compgeom.algo.bounding import (
    largest_empty_circle,
    largest_empty_sphere,
    largest_empty_oriented_rectangle,
    largest_empty_oriented_box,
    largest_empty_oriented_ellipse,
    largest_empty_oriented_ellipsoid
)

def test_largest_empty_circle():
    # Square with a point in the center
    points = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10), Point2D(5, 5)]
    center, radius = largest_empty_circle(points)
    # The Delaunay triangles are (0,0,10,0,5,5), etc.
    # For (0,0,10,0,5,5), circumcenter is (5,0), radius is 5.
    assert center.x == pytest.approx(5.0)
    assert radius == pytest.approx(5.0)

def test_largest_empty_sphere():
    # Cube with a point in the center
    points = [
        Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0),
        Point3D(0, 0, 10), Point3D(10, 0, 10), Point3D(10, 10, 10), Point3D(0, 10, 10),
        Point3D(5, 5, 5)
    ]
    center, radius = largest_empty_sphere(points)
    # Similar to 2D, one optimal sphere is centered on a face
    assert radius == pytest.approx(5.0)

def test_largest_empty_oriented_rectangle():
    # A rectangle where one half is empty
    points = [
        Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10),
        Point2D(2, 5) # Point blocking the left side
    ]
    result = largest_empty_oriented_rectangle(points)
    assert result['area'] == pytest.approx(80.0) # 8x10 rectangle on the right
    assert result['width'] * result['height'] == pytest.approx(80.0)

def test_largest_empty_oriented_box():
    # A cube where one section is empty
    points = [
        Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0),
        Point3D(0, 0, 10), Point3D(10, 0, 10), Point3D(10, 10, 10), Point3D(0, 10, 10),
        Point3D(2, 5, 5) # Blocking point
    ]
    result = largest_empty_oriented_box(points)
    assert result['volume'] == pytest.approx(800.0) # 8x10x10 box
    assert result['width'] * result['height'] * result['depth'] == pytest.approx(800.0)

def test_largest_empty_oriented_ellipse():
    points = [
        Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10),
        Point2D(2, 5)
    ]
    result = largest_empty_oriented_ellipse(points)
    assert result['area'] > 0
    assert result['center'] is not None

def test_largest_empty_oriented_ellipsoid():
    points = [
        Point3D(0, 0, 0), Point3D(10, 0, 0), Point3D(10, 10, 0), Point3D(0, 10, 0),
        Point3D(0, 0, 10), Point3D(10, 0, 10), Point3D(10, 10, 10), Point3D(0, 10, 10),
        Point3D(5, 5, 5)
    ]
    result = largest_empty_oriented_ellipsoid(points)
    assert result['volume'] > 0
    assert result['center'] is not None

