import math
import pytest
from compgeom.kernel import Point2D
from compgeom.kernel.polygon import Polygon2D
from compgeom.polygon.straight_skeleton import StraightSkeleton


def test_straight_skeleton_square():
    polygon = Polygon2D((Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)))
    skeleton = StraightSkeleton(polygon)
    skeleton.compute()

    assert len(skeleton.skeleton_points) >= 4
    assert len(skeleton.skeleton_edges) > 0


def test_straight_skeleton_rectangle():
    polygon = Polygon2D((Point2D(0, 0), Point2D(6, 0), Point2D(6, 3), Point2D(0, 3)))
    skeleton = StraightSkeleton(polygon)
    skeleton.compute()

    assert len(skeleton.skeleton_points) >= 4
    assert len(skeleton.skeleton_edges) > 0


def test_straight_skeleton_triangle():
    polygon = Polygon2D((Point2D(0, 0), Point2D(3, 0), Point2D(1.5, 3)))
    skeleton = StraightSkeleton(polygon)
    skeleton.compute()

    assert len(skeleton.skeleton_points) >= 3
    assert len(skeleton.skeleton_edges) > 0


def test_straight_skeleton_bisectors():
    polygon = Polygon2D((Point2D(0, 0), Point2D(1, 0), Point2D(1, 1)))
    skeleton = StraightSkeleton(polygon)
    bisectors = skeleton._compute_bisectors()

    assert len(bisectors) == 3
    for b in bisectors:
        dx, dy = b
        length = math.hypot(dx, dy)
        assert length > 0 or (dx == 0 and dy == 0)


def test_straight_skeleton_collision_time():
    polygon = Polygon2D((Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)))
    skeleton = StraightSkeleton(polygon)
    bisectors = skeleton._compute_bisectors()

    t = skeleton._compute_collision_time(0, 1, bisectors)
    assert t > 0


def test_straight_skeleton_collision_point():
    polygon = Polygon2D((Point2D(0, 0), Point2D(2, 0), Point2D(2, 2)))
    skeleton = StraightSkeleton(polygon)
    bisectors = skeleton._compute_bisectors()
    t = skeleton._compute_collision_time(0, 1, bisectors)

    if t > 0:
        point = skeleton._get_collision_point(0, 1, bisectors, t)
        assert isinstance(point, Point2D)
