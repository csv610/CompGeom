import pytest
from compgeom.kernel import Point2D
from compgeom.spatial.kinetic_voronoi import KineticPoint, KineticVoronoi


def test_kinetic_point_creation():
    p = KineticPoint(Point2D(0, 0), (1.0, 2.0))
    assert p.p0 == Point2D(0, 0)
    assert p.v == (1.0, 2.0)


def test_kinetic_point_pos():
    p = KineticPoint(Point2D(0, 0), (1.0, 1.0))
    pos_t0 = p.pos(0.0)
    pos_t1 = p.pos(1.0)
    pos_t2 = p.pos(2.0)

    assert pos_t0 == Point2D(0, 0)
    assert pos_t1 == Point2D(1, 1)
    assert pos_t2 == Point2D(2, 2)


def test_kinetic_point_negative_velocity():
    p = KineticPoint(Point2D(5, 5), (-1.0, -0.5))
    pos_t5 = p.pos(5.0)
    assert pos_t5 == Point2D(0, 2.5)


def test_kinetic_voronoi_creation():
    points = [
        KineticPoint(Point2D(0, 0), (1, 0)),
        KineticPoint(Point2D(10, 0), (-1, 0)),
        KineticPoint(Point2D(5, 10), (0, -1)),
    ]
    kd = KineticVoronoi(points)
    assert kd.current_time == 0.0
    assert len(kd.points) == 3


def test_kinetic_voronoi_get_current_triangulation():
    points = [
        KineticPoint(Point2D(0, 0), (0.5, 0)),
        KineticPoint(Point2D(10, 0), (-0.5, 0)),
        KineticPoint(Point2D(5, 10), (0, -0.5)),
    ]
    kd = KineticVoronoi(points)
    triangles = kd.get_current_triangulation()
    assert triangles is not None
    assert hasattr(triangles, "faces") or hasattr(triangles, "triangles")


def test_kinetic_voronoi_advance_to():
    points = [
        KineticPoint(Point2D(0, 0), (1, 0)),
        KineticPoint(Point2D(10, 0), (-1, 0)),
        KineticPoint(Point2D(5, 10), (0, -1)),
    ]
    kd = KineticVoronoi(points)
    kd.advance_to(1.0)
    assert kd.current_time == 1.0


def test_kinetic_voronoi_advance_to_zero():
    points = [
        KineticPoint(Point2D(0, 0), (1, 1)),
        KineticPoint(Point2D(5, 5), (-1, -1)),
    ]
    kd = KineticVoronoi(points)
    initial_time = kd.current_time
    kd.advance_to(0.0)
    assert kd.current_time == 0.0


def test_kinetic_voronoi_advance_past_events():
    points = [
        KineticPoint(Point2D(0, 0), (0, 0)),
        KineticPoint(Point2D(10, 0), (0, 0)),
        KineticPoint(Point2D(5, 10), (0, 0)),
    ]
    kd = KineticVoronoi(points)
    kd.advance_to(100.0)
    assert kd.current_time == 100.0
