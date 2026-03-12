import pytest
import math
from compgeom.kernel import (
    Point, Point3D,
    cross_product, orientation, orientation_sign, dot_product,
    sub, length_sq, length, distance, distance_3d, signed_area_twice,
    rotate_2d, unrotate_2d, support, get_circle_two_points, get_circle_three_points,
    incircle_det, incircle_sign, in_circle, triangle_area, triangle_circumcenter,
    triangle_incenter, triangle_inradius, contains_point,
    circle_area, circle_perimeter, is_convex_quad, quad_area, segment_midpoint
)
from compgeom.algo.space_filling_curves import (
    _peano_index_to_coords,
    _morton_index_to_coords,
    _hilbert_index_to_coords
)

def test_cross_product():
    origin = Point(0, 0)
    a = Point(1, 0)
    b = Point(0, 1)
    assert cross_product(origin, a, b) == 1.0
    assert cross_product(origin, b, a) == -1.0

def test_orientation():
    a = Point(0, 0)
    b = Point(1, 0)
    c = Point(0, 1)
    assert orientation(a, b, c) > 0
    assert orientation(a, c, b) < 0
    assert orientation(a, b, Point(2, 0)) == 0.0

def test_orientation_sign():
    a = Point(0, 0)
    b = Point(1, 0)
    c = Point(0, 1)
    assert orientation_sign(a, b, c) == 1
    assert orientation_sign(a, c, b) == -1
    assert orientation_sign(a, b, Point(2, 0)) == 0

def test_dot_product():
    a = Point(1, 2)
    b = Point(3, 4)
    assert dot_product(a, b) == 11.0

def test_sub():
    a = Point(3, 4)
    b = Point(1, 2)
    c = sub(a, b)
    assert c.x == 2 and c.y == 2

def test_length_sq():
    a = Point(3, 4)
    assert length_sq(a) == 25.0

def test_length():
    a = Point(3, 4)
    assert length(a) == 5.0

def test_distance():
    a = Point(0, 0)
    b = Point(3, 4)
    assert distance(a, b) == 5.0

def test_distance_3d():
    a = Point3D(0, 0, 0)
    b = Point3D(2, 3, 6)
    assert distance_3d(a, b) == 7.0

def test_signed_area_twice():
    polygon = [Point(0, 0), Point(2, 0), Point(0, 2)]
    assert signed_area_twice(polygon) == 4.0
    polygon_cw = [Point(0, 0), Point(0, 2), Point(2, 0)]
    assert signed_area_twice(polygon_cw) == -4.0

def test_rotate_unrotate():
    p = Point(1, 0)
    theta = math.pi / 2
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    rotated = rotate_2d(p, cos_t, sin_t)
    assert math.isclose(rotated.x, 0, abs_tol=1e-9)
    assert math.isclose(rotated.y, -1, abs_tol=1e-9)
    
    unrotated = unrotate_2d(rotated, cos_t, sin_t)
    assert math.isclose(unrotated.x, 1, abs_tol=1e-9)
    assert math.isclose(unrotated.y, 0, abs_tol=1e-9)

def test_support():
    polygon = [Point(0, 0), Point(2, 0), Point(1, 2)]
    dir = Point(0, 1)
    sup = support(polygon, dir)
    assert sup == Point(1, 2)

def test_get_circle_two_points():
    p1 = Point(-1, 0)
    p2 = Point(1, 0)
    center, radius = get_circle_two_points(p1, p2)
    assert center.x == 0 and center.y == 0
    assert radius == 1.0

def test_get_circle_three_points():
    p1 = Point(-1, 0)
    p2 = Point(1, 0)
    p3 = Point(0, 1)
    center, radius = get_circle_three_points(p1, p2, p3)
    assert math.isclose(center.x, 0, abs_tol=1e-9)
    assert math.isclose(center.y, 0, abs_tol=1e-9)
    assert math.isclose(radius, 1.0, abs_tol=1e-9)

def test_in_circle():
    a = Point(-1, 0)
    b = Point(1, 0)
    c = Point(0, 1)
    d_in = Point(0, 0)
    d_out = Point(0, 2)
    d_on = Point(0, -1)
    
    assert in_circle(a, b, c, d_in) == True
    assert in_circle(a, b, c, d_out) == False
    assert incircle_sign(a, b, c, d_on) == 0

def test_triangle_props():
    a = Point(0, 0)
    b = Point(2, 0)
    c = Point(0, 2)
    assert triangle_area(a, b, c) == 2.0
    assert triangle_inradius(a, b, c) > 0
    assert triangle_incenter(a, b, c) is not None
    assert triangle_circumcenter(a, b, c) == Point(1, 1)

def test_circle_props():
    assert math.isclose(circle_area(1.0), math.pi)
    assert math.isclose(circle_perimeter(1.0), 2 * math.pi)

def test_quad_props():
    p1, p2, p3, p4 = Point(0,0), Point(2,0), Point(2,2), Point(0,2)
    assert quad_area(p1, p2, p3, p4) == 4.0
    assert is_convex_quad(p1, p2, p3, p4) is True
    assert is_convex_quad(Point(0,0), Point(2,0), Point(1,1), Point(0,2)) is False

def test_segment_props():
    assert segment_midpoint(Point(0,0), Point(2,2)) == Point(1,1)

def test_space_filling_curves():
    # Peano
    assert _peano_index_to_coords(0, 1) == (0, 0)
    # Morton
    assert _morton_index_to_coords(0) == (0, 0)
    assert _morton_index_to_coords(3) == (1, 1)
    # Hilbert
    assert _hilbert_index_to_coords(0, 1) == (0, 0)
