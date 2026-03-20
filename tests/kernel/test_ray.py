
import math
import pytest
from compgeom.kernel.point import Point2D, Point3D
from compgeom.kernel.ray import Ray

def test_ray_initialization_2d():
    origin = Point2D(0, 0)
    direction = Point2D(2, 0)
    ray = Ray(origin, direction)
    assert ray.origin == origin
    assert ray.direction.x == pytest.approx(1.0)
    assert ray.direction.y == pytest.approx(0.0)

def test_ray_initialization_3d():
    origin = Point3D(1, 2, 3)
    direction = Point3D(0, 3, 4)
    ray = Ray(origin, direction)
    assert ray.origin == origin
    assert ray.direction.x == pytest.approx(0.0)
    assert ray.direction.y == pytest.approx(3.0 / 5.0)
    assert ray.direction.z == pytest.approx(4.0 / 5.0)

def test_ray_zero_direction():
    with pytest.raises(ValueError, match="Direction vector cannot be zero."):
        Ray(Point2D(0, 0), Point2D(0, 0))

def test_point_at():
    ray = Ray(Point2D(1, 1), Point2D(1, 0))
    assert ray.point_at(0) == Point2D(1, 1)
    assert ray.point_at(5) == Point2D(6, 1)
    assert ray.point_at(-1) == Point2D(1, 1) # Clamped to origin

def test_closest_parameter_and_point():
    ray = Ray(Point2D(0, 0), Point2D(1, 0))
    # Point ahead
    p1 = Point2D(5, 5)
    assert ray.closest_parameter(p1) == pytest.approx(5.0)
    assert ray.closest_point(p1) == Point2D(5, 0)
    # Point behind
    p2 = Point2D(-2, 10)
    assert ray.closest_parameter(p2) == pytest.approx(0.0)
    assert ray.closest_point(p2) == Point2D(0, 0)

def test_distance_to():
    ray = Ray(Point2D(0, 0), Point2D(0, 1))
    p1 = Point2D(3, 5)
    assert ray.distance_to(p1) == pytest.approx(3.0)
    p2 = Point2D(4, -2) # Behind origin
    assert ray.distance_to(p2) == pytest.approx(math.sqrt(4**2 + 2**2))

def test_contains_point():
    ray = Ray(Point2D(0, 0), Point2D(1, 1))
    assert ray.contains_point(Point2D(0, 0)) is True
    assert ray.contains_point(Point2D(2, 2)) is True
    assert ray.contains_point(Point2D(-1, -1)) is False # Behind
    assert ray.contains_point(Point2D(1, 0)) is False # Off ray

def test_intersect_sphere_3d():
    # Sphere at (10, 0, 0) with radius 2
    center = Point3D(10, 0, 0)
    radius = 2.0
    
    # Ray hitting head-on
    ray1 = Ray(Point3D(0, 0, 0), Point3D(1, 0, 0))
    intersections = ray1.intersect_sphere(center, radius)
    assert intersections is not None
    t1, t2 = intersections
    assert t1 == pytest.approx(8.0)
    assert t2 == pytest.approx(12.0)
    
    # Ray missing
    ray2 = Ray(Point3D(0, 5, 0), Point3D(1, 0, 0))
    assert ray2.intersect_sphere(center, radius) is None
    
    # Ray starting inside
    ray3 = Ray(Point3D(10, 0, 0), Point3D(0, 1, 0))
    intersections = ray3.intersect_sphere(center, radius)
    assert intersections is not None
    t1, t2 = intersections
    assert t1 == pytest.approx(0.0)
    assert t2 == pytest.approx(2.0)
    
    # Ray pointing away
    ray4 = Ray(Point3D(15, 0, 0), Point3D(1, 0, 0))
    assert ray4.intersect_sphere(center, radius) is None

def test_repr():
    ray = Ray(Point2D(0, 0), Point2D(1, 0))
    assert "Ray" in repr(ray)
    assert "o=P-1(0, 0)" in repr(ray)
