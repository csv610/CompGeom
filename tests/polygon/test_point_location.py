import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.point_location import Trapezoid, TrapezoidNode, TrapezoidalMap


def test_trapezoid_creation():
    top_edge = (Point2D(0, 1), Point2D(2, 1))
    bottom_edge = (Point2D(0, 0), Point2D(2, 0))
    trap = Trapezoid(Point2D(0, 0), Point2D(2, 0), top_edge, bottom_edge)

    assert trap.left == Point2D(0, 0)
    assert trap.right == Point2D(2, 0)
    assert trap.top_edge == top_edge
    assert trap.bottom_edge == bottom_edge


def test_trapezoid_node_leaf():
    top_edge = (Point2D(0, 1), Point2D(2, 1))
    bottom_edge = (Point2D(0, 0), Point2D(2, 0))
    trap = Trapezoid(Point2D(0, 0), Point2D(2, 0), top_edge, bottom_edge)
    node = TrapezoidNode(trap)

    assert node.is_leaf() is True
    assert node.is_x_node() is False
    assert node.is_y_node() is False


def test_trapezoid_node_x():
    node = TrapezoidNode(Point2D(1, 1))

    assert node.is_x_node() is True
    assert node.is_y_node() is False
    assert node.is_leaf() is False


def test_trapezoid_node_y():
    node = TrapezoidNode((Point2D(0, 0), Point2D(1, 1)))

    assert node.is_y_node() is True
    assert node.is_x_node() is False
    assert node.is_leaf() is False


def test_trapezoidal_map_creation():
    bbox = (Point2D(0, 0), Point2D(10, 10))
    tmap = TrapezoidalMap(bbox)

    assert tmap.bounding_box == bbox
    assert tmap.root is not None
    assert tmap.root.is_leaf() is True


def test_trapezoidal_map_locate_point_inside():
    bbox = (Point2D(0, 0), Point2D(10, 10))
    tmap = TrapezoidalMap(bbox)

    result = tmap.locate(Point2D(5, 5))
    assert result is not None
    assert isinstance(result, Trapezoid)


def test_trapezoidal_map_locate_boundary():
    bbox = (Point2D(0, 0), Point2D(10, 10))
    tmap = TrapezoidalMap(bbox)

    result = tmap.locate(Point2D(0, 5))
    assert result is not None


def test_trapezoidal_map_locate_outside():
    bbox = (Point2D(0, 0), Point2D(10, 10))
    tmap = TrapezoidalMap(bbox)

    result = tmap.locate(Point2D(15, 15))
    assert result is not None
    assert isinstance(result, Trapezoid)


def test_trapezoidal_map_is_above():
    bbox = (Point2D(0, 0), Point2D(10, 10))
    tmap = TrapezoidalMap(bbox)

    edge = (Point2D(0, 0), Point2D(10, 0))
    assert tmap._is_above(Point2D(5, 1), edge) is True
    assert tmap._is_above(Point2D(5, -1), edge) is False
