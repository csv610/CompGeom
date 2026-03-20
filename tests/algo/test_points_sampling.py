
import math
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.algo import points_sampling

def test_sampler_circle():
    center = Point2D(5, 5)
    radius = 2.0
    # in_circle
    pts_in = points_sampling.PointSampler.in_circle(center, radius, n_points=10)
    assert len(pts_in) == 10
    for p in pts_in:
        assert math.hypot(p.x - center.x, p.y - center.y) <= radius + 1e-9
    
    # on_circle
    pts_on = points_sampling.PointSampler.on_circle(center, radius, n_points=10)
    assert len(pts_on) == 10
    for p in pts_on:
        assert math.hypot(p.x - center.x, p.y - center.y) == pytest.approx(radius)

def test_sampler_rectangle():
    center = Point2D(0, 0)
    w, h = 10, 4
    # in_rectangle
    pts_in = points_sampling.PointSampler.in_rectangle(w, h, n_points=10, center=center)
    assert len(pts_in) == 10
    for p in pts_in:
        assert -5 <= p.x <= 5
        assert -2 <= p.y <= 2
        
    # on_rectangle
    pts_on = points_sampling.PointSampler.on_rectangle(w, h, n_points=20, center=center)
    assert len(pts_on) == 20
    for p in pts_on:
        # Should be on one of the 4 edges
        on_edge = (abs(p.x - 5) < 1e-9 or abs(p.x + 5) < 1e-9 or 
                   abs(p.y - 2) < 1e-9 or abs(p.y + 2) < 1e-9)
        assert on_edge

def test_sampler_triangle():
    a, b, c = Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)
    pts = points_sampling.PointSampler.in_triangle(a, b, c, n_points=10)
    assert len(pts) == 10
    # Check that points are in triangle (x+y <= 1 and x,y >= 0)
    for p in pts:
        assert p.x >= -1e-9
        assert p.y >= -1e-9
        assert p.x + p.y <= 1.0 + 1e-9

def test_sampler_line_segment():
    p1, p2 = Point2D(0, 0), Point2D(10, 10)
    pts = points_sampling.PointSampler.on_line_segment(p1, p2, n_points=10)
    assert len(pts) == 10
    for p in pts:
        assert pytest.approx(p.x) == p.y
        assert 0 <= p.x <= 10

def test_sampler_cube():
    center = Point3D(0, 0, 0)
    pts = points_sampling.PointSampler.in_cube(side_length=2.0, n_points=10, center=center)
    assert len(pts) == 10
    for p in pts:
        assert -1 <= p.x <= 1
        assert -1 <= p.y <= 1
        assert -1 <= p.z <= 1

def test_sampler_sphere():
    center = Point3D(0, 0, 0)
    radius = 5.0
    pts = points_sampling.PointSampler.on_sphere(center, radius, n_points=10)
    assert len(pts) == 10
    for p in pts:
        dist = math.sqrt(p.x**2 + p.y**2 + p.z**2)
        assert dist == pytest.approx(radius)

def test_wrappers():
    c = Point2D(0, 0)
    assert len(points_sampling.generate_points_in_circle(c, 1.0)) == 100
    assert len(points_sampling.generate_points_in_rectangle(1.0, 1.0)) == 100
