import pytest

from compgeom.algo.point_trees import Interval, IntervalTree, SegmentTree, build_kdtree, range_search
from compgeom.kernel import Point2D


def test_kdtree_range_search_returns_points_in_rectangle():
    points = [
        Point2D(0, 0),
        Point2D(1, 2),
        Point2D(2, 1),
        Point2D(3, 3),
        Point2D(4, 0),
    ]
    root = build_kdtree(points)

    result = range_search(root, 1, 3, 1, 3)

    assert sorted((point.x, point.y) for point in result) == [(1, 2), (2, 1), (3, 3)]


def test_interval_tree_supports_point_and_interval_queries():
    tree = IntervalTree(
        [
            Interval(0, 3, "a"),
            Interval(2, 6, "b"),
            Interval(5, 8, "c"),
            (7, 9, "d"),
        ]
    )

    point_hits = tree.query_point(5)
    interval_hits = tree.query_interval(4, 7)

    assert {interval.payload for interval in point_hits} == {"b", "c"}
    assert {interval.payload for interval in interval_hits} == {"b", "c", "d"}


def test_interval_tree_rejects_invalid_intervals_and_query_ranges():
    with pytest.raises(ValueError):
        Interval(4, 1)

    tree = IntervalTree([Interval(0, 2), Interval(3, 5)])
    with pytest.raises(ValueError):
        tree.query_interval(6, 4)


def test_segment_tree_sum_query_and_update():
    tree = SegmentTree.for_sum([2, 1, 3, 4, 5])

    assert tree.range_query(1, 3) == 8

    tree.update(2, 10)

    assert tree.range_query(1, 3) == 15
    assert tree.range_query(0, 4) == 22


def test_segment_tree_min_and_max_helpers():
    min_tree = SegmentTree.for_min([7, 2, 9, 4])
    max_tree = SegmentTree.for_max([7, 2, 9, 4])

    assert min_tree.range_query(1, 3) == 2
    assert max_tree.range_query(1, 3) == 9


def test_segment_tree_rejects_invalid_ranges_and_indices():
    tree = SegmentTree.for_sum([1, 2, 3])

    with pytest.raises(IndexError):
        tree.update(3, 10)

    with pytest.raises(IndexError):
        tree.range_query(1, 3)


def test_range_search_returns_empty_for_empty_tree():
    assert range_search(None, 0, 1, 0, 1) == []
