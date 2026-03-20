
import math
import pytest
from compgeom.kernel.point import Point3D
from compgeom.kernel.plane import Plane

# A simple mock for Ray3D since ray.py is not yet tested
class MockRay3D:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

@pytest.fixture
def xy_plane():
    """A plane on z=0, with normal pointing up."""
    return Plane.from_point_and_normal(Point3D(5, 5, 0), Point3D(0, 0, 1))

@pytest.fixture
def yz_plane():
    """A plane on x=0."""
    return Plane.from_point_and_normal(Point3D(0, 1, 2), Point3D(1, 0, 0))

def test_from_point_and_normal(xy_plane):
    assert xy_plane.normal == Point3D(0, 0, 1)
    assert xy_plane.d == pytest.approx(0)
    
    # Test a shifted plane
    plane = Plane.from_point_and_normal(Point3D(1, 2, 3), Point3D(0, 1, 0))
    assert plane.normal == Point3D(0, 1, 0)
    assert plane.d == pytest.approx(-2)
    
    # Test zero normal
    with pytest.raises(ValueError):
        Plane.from_point_and_normal(Point3D(1,1,1), Point3D(0,0,0))

def test_from_points():
    p1, p2, p3 = Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 0)
    plane = Plane.from_points(p1, p2, p3)
    # Normal should be parallel to z-axis
    assert abs(plane.normal.dot(Point3D(0,0,1))) == pytest.approx(1.0)
    assert plane.d == pytest.approx(0)

    # Collinear points
    with pytest.raises(ValueError):
        Plane.from_points(Point3D(0,0,0), Point3D(1,1,1), Point3D(2,2,2))

def test_distance_and_side(xy_plane):
    p_above = Point3D(10, -5, 3)
    p_below = Point3D(10, -5, -4)
    p_on = Point3D(10, -5, 0)
    
    # signed_distance and distance
    assert xy_plane.signed_distance(p_above) == pytest.approx(3.0)
    assert xy_plane.distance(p_above) == pytest.approx(3.0)
    assert xy_plane.signed_distance(p_below) == pytest.approx(-4.0)
    assert xy_plane.distance(p_below) == pytest.approx(4.0)

    # is_on_plane and side
    assert xy_plane.is_on_plane(p_on) is True
    assert xy_plane.side(p_on) == 0
    assert xy_plane.is_on_plane(p_above) is False
    assert xy_plane.side(p_above) == 1
    assert xy_plane.is_on_plane(p_below) is False
    assert xy_plane.side(p_below) == -1

def test_project_point(xy_plane):
    p = Point3D(10, -5, 3)
    p_proj = xy_plane.project_point(p)
    assert p_proj == Point3D(10, -5, 0)

def test_intersect_ray(xy_plane):
    # Ray pointing down at the plane
    ray1 = MockRay3D(origin=Point3D(5, 5, 10), direction=Point3D(0, 0, -1))
    t1 = xy_plane.intersect_ray(ray1)
    assert t1 == pytest.approx(10.0)

    # Ray parallel to the plane
    ray2 = MockRay3D(origin=Point3D(5, 5, 10), direction=Point3D(1, 0, 0))
    assert xy_plane.intersect_ray(ray2) is None

    # Ray pointing away from the plane
    ray3 = MockRay3D(origin=Point3D(5, 5, 10), direction=Point3D(0, 0, 1))
    assert xy_plane.intersect_ray(ray3) is None
    
    # Ray starting on the plane
    ray4 = MockRay3D(origin=Point3D(5, 5, 0), direction=Point3D(1, 1, 1))
    assert xy_plane.intersect_ray(ray4) == pytest.approx(0.0)

def test_intersect_plane(xy_plane, yz_plane):
    # Intersect z=0 and x=0 planes
    res = xy_plane.intersect_plane(yz_plane)
    assert res is not None
    point, direction = res
    
    # The line of intersection is the y-axis
    # Check that direction is parallel to y-axis
    assert abs(direction.dot(Point3D(0, 1, 0))) == pytest.approx(1.0)
    # Check that the point is on the y-axis (x=0 and z=0)
    assert abs(point.x) < 1e-9
    assert abs(point.z) < 1e-9

    # Parallel planes
    plane_z1 = Plane.from_point_and_normal(Point3D(0,0,1), Point3D(0,0,1))
    assert xy_plane.intersect_plane(plane_z1) is None
