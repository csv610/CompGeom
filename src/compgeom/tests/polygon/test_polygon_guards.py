from compgeom.kernel import Point2D
from compgeom.polygon import PolygonGuards, guard_polygon, solve_art_gallery


def test_solve_art_gallery_returns_one_guard_for_triangle():
    polygon = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]

    guards = solve_art_gallery(polygon)

    assert len(guards) == 1
    assert guards[0] in polygon


def test_solve_art_gallery_returns_one_guard_for_square():
    polygon = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]

    guards = solve_art_gallery(polygon)

    assert len(guards) == 1
    assert guards[0] in polygon


def test_solve_art_gallery_respects_chvatal_bound_for_l_shaped_polygon():
    polygon = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(2, 1),
        Point2D(1, 1),
        Point2D(1, 2),
        Point2D(0, 2),
    ]

    guards = solve_art_gallery(polygon)

    assert 1 <= len(guards) <= 2
    assert set(guards).issubset(set(polygon))


def test_guard_polygon_returns_empty_list_for_empty_triangulation():
    assert guard_polygon([], []) == []
    assert PolygonGuards.guard_polygon([], []) == []
