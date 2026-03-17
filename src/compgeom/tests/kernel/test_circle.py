import pytest
import math
import fractions
from decimal import Decimal
from compgeom.kernel.point import Point2D
from compgeom.kernel.circle import (
    Circle2D,
    area as circle_area,
    perimeter as circle_perimeter,
    in_circle, incircle_sign, incircle_det, robust_in_circle,
    from_two_points as circle_from_two_points,
    from_three_points as circle_from_three_points,
    common_tangents, tangents_from_point
)
from compgeom.kernel.math_utils import distance

def test_circle_2d_basics():
    c = Point2D(0, 0)
    r = 5.0
    circle = Circle2D(c, r)
    assert circle.center == c
    assert circle.radius == r
    assert math.isclose(circle.area(), math.pi * 25.0)
    assert math.isclose(circle.perimeter(), 2 * math.pi * 5.0)
    assert circle.contains_point(Point2D(3, 4))
    assert circle.contains_point(Point2D(5, 0))
    assert not circle.contains_point(Point2D(5.1, 0))
    assert "Circle2D" in repr(circle)

def test_circle_standalone_props():
    assert math.isclose(circle_area(1.0), math.pi)
    assert math.isclose(circle_perimeter(1.0), 2 * math.pi)

def test_from_two_points():
    p1 = Point2D(-1, 0)
    p2 = Point2D(1, 0)
    center, radius = circle_from_two_points(p1, p2)
    assert center.x == 0 and center.y == 0
    assert radius == 1.0

def test_from_three_points():
    p1 = Point2D(-1, 0)
    p2 = Point2D(1, 0)
    p3 = Point2D(0, 1)
    center, radius = circle_from_three_points(p1, p2, p3)
    assert math.isclose(center.x, 0, abs_tol=1e-9)
    assert math.isclose(center.y, 0, abs_tol=1e-9)
    assert math.isclose(radius, 1.0, abs_tol=1e-9)

    # Collinear points fallback: smallest circle of two furthest points
    p4 = Point2D(2, 0)
    # p1=(-1,0), p2=(1,0), p4=(2,0) are collinear
    # furthest are p1 and p4
    center2, radius2 = circle_from_three_points(p1, p2, p4)
    assert center2.x == 0.5
    assert center2.y == 0
    assert radius2 == 1.5

def test_in_circle_predicates():
    a = Point2D(-1, 0)
    b = Point2D(1, 0)
    c = Point2D(0, 1)
    d_in = Point2D(0, 0)
    d_out = Point2D(0, 2)
    d_on = Point2D(0, -1)
    
    assert in_circle(a, b, c, d_in) == True
    assert in_circle(a, b, c, d_out) == False
    assert incircle_sign(a, b, c, d_on) == 0
    assert abs(incircle_det(a, b, c, d_on)) < 1e-15

def test_robust_in_circle():
    # Simple cases
    a = Point2D(0, 0, id=0)
    b = Point2D(1, 0, id=1)
    c = Point2D(0, 1, id=2)
    
    # Inside point (0.1, 0.1)
    assert robust_in_circle(a, b, c, Point2D(0.1, 0.1, id=3)) == True
    # Outside point (1, 1)
    assert robust_in_circle(a, b, c, Point2D(1, 1, id=4)) == False
    
    # SOS Tie-break case (4 points on circle)
    # a=(0,0), b=(1,0), c=(0,1) -> circumcircle center (0.5, 0.5), r^2 = 0.5
    # Point (1,1) is on this circle.
    
    # Case: d.id is max
    assert robust_in_circle(a, b, c, Point2D(1, 1, id=3)) == False
    
    # Case: a.id is max
    a2 = Point2D(0, 0, id=4)
    assert robust_in_circle(a2, b, c, Point2D(1, 1, id=3)) == True

def test_tangents_from_point():
    circle = Circle2D(Point2D(0, 0), 1.0)
    
    # Point outside
    p = Point2D(2, 0)
    tangents = tangents_from_point(circle, p)
    assert len(tangents) == 2
    # Tangent points should be at distance 1 from origin
    for t in tangents:
        assert math.isclose(distance(Point2D(0,0), t.end), 1.0)
        # Tangent line should be perpendicular to radius CT
        # Vector CP dot vector CT = R^2 = 1
        # Vector CT dot vector TP = 0
        v_ct = Point2D(t.end.x - circle.center.x, t.end.y - circle.center.y)
        v_tp = Point2D(p.x - t.end.x, p.y - t.end.y)
        dot = v_ct.x * v_tp.x + v_ct.y * v_tp.y
        assert math.isclose(dot, 0, abs_tol=1e-9)

    # Point on circle
    p_on = Point2D(1, 0)
    tangents_on = tangents_from_point(circle, p_on)
    assert len(tangents_on) == 1
    assert tangents_on[0].start == p_on
    assert tangents_on[0].end == p_on

    # Point inside circle
    p_in = Point2D(0.5, 0)
    assert len(tangents_from_point(circle, p_in)) == 0

def test_common_tangents():
    c1 = Circle2D(Point2D(0, 0), 1.0)
    c2 = Circle2D(Point2D(4, 0), 1.0)
    
    # Two equal circles separated: 2 external, 2 internal
    tangents = common_tangents(c1, c2)
    assert len(tangents) == 4
    
    # concentric circles
    assert len(common_tangents(c1, Circle2D(Point2D(0,0), 2.0))) == 0

    # Touching circles (external)
    c3 = Circle2D(Point2D(2, 0), 1.0) # Tangent at (1,0)
    # distance between centers is 2, sum of radii is 2.
    # 2 external, 1 internal (at point of contact)
    # wait, sr <= d + epsilon: sr = 2, d = 2. 
    # Internal tangents calculation should give one if cos_beta = 1.
    tangents_touching = common_tangents(c1, c3)
    # r1+r2 = 2, d=2. cos_beta = 1. beta = 0.
    # a = alpha = 0.
    # p1 = (1,0), a2 = pi, p2 = (2-1, 0) = (1,0)
    # res.append(LineSegment((1,0), (1,0)))
    assert len(tangents_touching) == 3 
