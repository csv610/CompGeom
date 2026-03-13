import pytest

from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, reorder_to_match


def test_reorder_to_match_aligns_cyclic_shifted_polygon():
    reference = Polygon([Point2D(0, 0), Point2D(10, 0), Point2D(5, 5)])
    shifted = Polygon([Point2D(5, 5), Point2D(0, 0), Point2D(10, 0)])

    reordered = reorder_to_match(reference, shifted)

    assert reordered == list(reference.vertices)
    assert reference.reorder_to_match(shifted) == list(reference.vertices)


def test_reorder_to_match_can_reflect_when_enabled():
    reference = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(1, 3)])
    reflected = Polygon([Point2D(0, 0), Point2D(1, 3), Point2D(2, 0)])

    reordered = reorder_to_match(reference, reflected, allow_reflection=True)

    assert reordered == list(reference.vertices)


def test_reorder_to_match_does_not_reflect_when_disabled():
    reference = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(1, 3)])
    reflected = Polygon([Point2D(0, 0), Point2D(1, 3), Point2D(2, 0)])

    reordered = reorder_to_match(reference, reflected, allow_reflection=False)

    assert reordered != list(reference.vertices)
    assert reordered in [
        list(reflected.vertices[i:]) + list(reflected.vertices[:i])
        for i in range(len(reflected.vertices))
    ]


def test_reorder_to_match_raises_for_mismatched_vertex_counts():
    triangle = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(1, 3)])
    square = Polygon([Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])

    with pytest.raises(ValueError, match="same number of vertices"):
        reorder_to_match(triangle, square)


def test_reorder_to_match_auto_clean_removes_redundant_points_before_matching():
    square = Polygon([Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])
    redundant = Polygon([Point2D(0, 0), Point2D(0.5, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])

    reordered = reorder_to_match(square, redundant, auto_clean=True)

    assert reordered == list(square.vertices)
    with pytest.raises(ValueError, match="same number of vertices"):
        reorder_to_match(square, redundant, auto_clean=False)
