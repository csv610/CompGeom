from __future__ import annotations

from typing import Sequence

from compgeom.kernel import Point2D, contains_point, cross_product
from compgeom.polygon.polygon import Polygon


def is_ear(a: Point2D, b: Point2D, c: Point2D, polygon: Sequence[Point2D]) -> bool:
    """Check if the triangle (a, b, c) is an ear of the polygon."""
    if cross_product(a, b, c) <= 0:
        return False

    class TriangleView:
        def __init__(self, v1: Point2D, v2: Point2D, v3: Point2D):
            self.vertices = (v1, v2, v3)

    triangle = TriangleView(a, b, c)
    for point in polygon:
        if point is not a and point is not b and point is not c:
            if contains_point(triangle, point):
                return False
    return True


def triangulate_polygon(
    polygon: list[Point2D], collect_diagonals: bool = False
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point2D]]:
    """Triangulates a simple polygon using ear clipping."""
    poly_obj = Polygon(polygon).ensure_ccw()
    ordered = poly_obj.as_list()
    polygon_size = len(ordered)
    working_polygon = list(ordered)
    working_indices = list(range(polygon_size))
    triangles: list[tuple[int, int, int]] = []
    diagonals: list[tuple[int, int]] = []

    while len(working_indices) > 3:
        for offset, current in enumerate(working_indices):
            prev_index = working_indices[offset - 1]
            next_index = working_indices[(offset + 1) % len(working_indices)]
            if not is_ear(
                ordered[prev_index],
                ordered[current],
                ordered[next_index],
                working_polygon,
            ):
                continue

            triangles.append((prev_index, current, next_index))
            if (
                collect_diagonals
                and abs(next_index - prev_index) != 1
                and {prev_index, next_index}
                != {
                    0,
                    polygon_size - 1,
                }
            ):
                diagonals.append(tuple(sorted((prev_index, next_index))))
            working_indices.pop(offset)
            working_polygon.pop(offset)
            break
        else:
            break

    if len(working_indices) == 3:
        triangles.append(tuple(working_indices))

    return triangles, diagonals, ordered
