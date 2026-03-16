from compgeom.kernel import Point2D
from compgeom.polygon import art_gallery_guards, guard_polygon


def test_art_gallery_guards_returns_one_guard_for_triangle():
    polygon = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]

    guards = art_gallery_guards(polygon)

    assert len(guards) == 1
    assert guards[0] in polygon


def test_art_gallery_guards_returns_one_guard_for_square():
    polygon = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]

    guards = art_gallery_guards(polygon)

    assert len(guards) == 1
    assert guards[0] in polygon


def test_art_gallery_guards_respects_chvatal_bound_for_l_shaped_polygon():
    polygon = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(2, 1),
        Point2D(1, 1),
        Point2D(1, 2),
        Point2D(0, 2),
    ]

    guards = art_gallery_guards(polygon)

    assert 1 <= len(guards) <= len(polygon) // 3
    assert set(guards).issubset(set(polygon))


def test_guard_polygon_returns_empty_list_for_empty_triangulation():
    assert guard_polygon([], []) == []


def test_art_gallery_guards_respects_chvatal_bound_for_comb_polygon():
    # Comb polygon with 4 spikes, n=20 vertices.
    # Base: (0,0) to (9,0), y from 0 to 1.
    # Spikes at x positions [1,2], [3,4], [5,6], [7,8], height up to y=3.
    polygon = [
        Point2D(0, 0), Point2D(9, 0), Point2D(9, 1),
        Point2D(8, 1), Point2D(8, 3), Point2D(7, 3), Point2D(7, 1),
        Point2D(6, 1), Point2D(6, 3), Point2D(5, 3), Point2D(5, 1),
        Point2D(4, 1), Point2D(4, 3), Point2D(3, 3), Point2D(3, 1),
        Point2D(2, 1), Point2D(2, 3), Point2D(1, 3), Point2D(1, 1),
        Point2D(0, 1)
    ]

    guards = art_gallery_guards(polygon)

    # Chvatal's theorem: floor(n/3) guards are always sufficient.
    # For n=20, floor(20/3) = 6.
    assert 1 <= len(guards) <= len(polygon) // 3
    assert set(guards).issubset(set(polygon))
