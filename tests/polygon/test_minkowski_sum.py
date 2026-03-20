from compgeom.kernel import Point2D
from compgeom.mesh import MinkowskiSum


def _canonical_cycle(points: list[Point2D]) -> list[Point2D]:
    if not points:
        return []

    first = points[0]
    for index in range(1, len(points)):
        if points[index] == first:
            return points[:index]

    for cycle_len in range(1, len(points) + 1):
        if len(points) % cycle_len != 0:
            continue
        cycle = points[:cycle_len]
        if cycle * (len(points) // cycle_len) == points:
            return cycle
    return points


def test_minkowski_sum_of_two_squares_returns_expected_square():
    square_a = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    square_b = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]

    result = MinkowskiSum.compute_convex(square_a, square_b)

    assert _canonical_cycle(result) == [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]


def test_minkowski_sum_of_rectangle_and_triangle_returns_expected_convex_polygon():
    rectangle = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(0, 1)]
    triangle = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 2)]

    result = MinkowskiSum.compute_convex(rectangle, triangle)

    assert _canonical_cycle(result) == [
        Point2D(0, 0),
        Point2D(3, 0),
        Point2D(3, 1),
        Point2D(2, 3),
        Point2D(0, 3),
    ]


def test_minkowski_sum_returns_empty_when_either_polygon_is_empty():
    polygon = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]

    assert MinkowskiSum.compute_convex([], polygon) == []
    assert MinkowskiSum.compute_convex(polygon, []) == []
