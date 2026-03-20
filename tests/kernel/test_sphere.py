
import math
import pytest
from compgeom.kernel.point import Point3D
from compgeom.kernel.sphere import Sphere, from_two_points, from_three_points, from_four_points, insphere_sign, in_sphere

def test_sphere_contains_point():
    center = Point3D(0, 0, 0)
    radius = 5.0
    s = Sphere(center, radius)
    p_inside = Point3D(3, 4, 0)
    p_outside = Point3D(6, 8, 0)
    p_on_surface = Point3D(5, 0, 0)
    assert s.contains_point(p_inside)
    assert not s.contains_point(p_outside)
    assert s.contains_point(p_on_surface)

def test_from_two_points():
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(10, 0, 0)
    s = from_two_points(p1, p2)
    assert s.center == Point3D(5, 0, 0)
    assert math.isclose(s.radius, 5.0)
    assert s.contains_point(p1)
    assert s.contains_point(p2)

def test_from_three_points_collinear():
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(5, 0, 0)
    p3 = Point3D(10, 0, 0)
    s = from_three_points(p1, p2, p3)
    # Should fallback to the two furthest points
    assert s.center == Point3D(5, 0, 0)
    assert math.isclose(s.radius, 5.0)

def test_from_three_points():
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(10, 0, 0)
    p3 = Point3D(5, 5, 0)
    s = from_three_points(p1, p2, p3)
    assert s.center == Point3D(5, 0, 0)
    assert math.isclose(s.radius, 5.0)
    assert s.contains_point(p1)
    assert s.contains_point(p2)
    assert s.contains_point(p3)

def test_from_four_points_coplanar():
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(10, 0, 0)
    p3 = Point3D(5, 5, 0)
    p4 = Point3D(5, -5, 0)
    s = from_four_points(p1, p2, p3, p4)
    # This should find the minimal sphere enclosing the 3 points that give the largest radius
    s1 = from_three_points(p1, p2, p3)
    s2 = from_three_points(p1, p2, p4)
    s3 = from_three_points(p1, p3, p4)
    s4 = from_three_points(p2, p3, p4)
    min_radius = min(s1.radius, s2.radius, s3.radius, s4.radius)
    assert math.isclose(s.radius, min_radius)

def test_from_four_points():
    p1 = Point3D(0, 0, 0)
    p2 = Point3D(2, 0, 0)
    p3 = Point3D(1, 1, 0)
    p4 = Point3D(1, 0.5, 1)
    s = from_four_points(p1, p2, p3, p4)
    assert s.contains_point(p1)
    assert s.contains_point(p2)
    assert s.contains_point(p3)
    assert s.contains_point(p4)

def test_insphere_sign_and_in_sphere():
    a = Point3D(0, 0, 0)
    b = Point3D(1, 0, 0)
    c = Point3D(0, 1, 0)
    d = Point3D(0, 0, 1)

    # Test point inside
    e_in = Point3D(0.1, 0.1, 0.1)
    assert insphere_sign(a, b, c, d, e_in) > 0
    assert in_sphere(a, b, c, d, e_in)

    # Test point outside
    e_out = Point3D(2, 2, 2) # This point is clearly outside
    assert insphere_sign(a, b, c, d, e_out) < 0
    assert not in_sphere(a, b, c, d, e_out)

    # Test point on sphere
    e_on = Point3D(1, 0, 0) # Same as b
    assert insphere_sign(a, b, c, d, e_on) == 0
    assert not in_sphere(a, b, c, d, e_on)

    # The sign should be invariant to orientation changes
    assert insphere_sign(b, a, c, d, e_in) == insphere_sign(a, b, c, d, e_in)
