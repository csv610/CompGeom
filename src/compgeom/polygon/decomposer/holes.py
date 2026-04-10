from __future__ import annotations

from compgeom.kernel import Point2D, distance
from compgeom.polygon.exceptions import HoleConnectionError
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_utils import segment_inside_boundaries
from .ear_clipping import triangulate_polygon


def triangulate_polygon_with_holes(
    outer_boundary: list[Point2D],
    holes: list[list[Point2D]] | None = None,
) -> tuple[list[tuple[Point2D, Point2D, Point2D]], list[Point2D]]:
    """Triangulates a polygonal domain with holes."""
    holes = holes or []
    # Create the merged polygon with bridges
    merged_polygon_list = list(Polygon(outer_boundary).ensure_ccw().as_list())
    for hole in holes:
        merged_polygon_list = _splice_hole(merged_polygon_list, Polygon(hole).ensure_cw().as_list())

    # Triangulate this merged polygon
    triangle_indices, _, _ = triangulate_polygon(merged_polygon_list)
    triangles = [
        tuple(merged_polygon_list[index] for index in triangle)
        for triangle in triangle_indices
    ]
    # We return the merged_polygon_list because it's the sequence of vertices 
    # forming the boundary (with bridges) of the triangulated domain.
    return triangles, merged_polygon_list


def _splice_hole(outer: list[Point2D], hole: list[Point2D]) -> list[Point2D]:
    hole_vertex_index = max(
        range(len(hole)), key=lambda index: (hole[index].x, -hole[index].y)
    )
    hole_vertex = hole[hole_vertex_index]

    candidates = []
    for outer_index, outer_vertex in enumerate(outer):
        if not _segment_inside_domain(
            outer, [hole], hole_vertex, outer_vertex, allow_hole_endpoint=hole_vertex
        ):
            continue
        candidates.append((distance(hole_vertex, outer_vertex), outer_index))
    if not candidates:
        raise HoleConnectionError("Failed to connect hole to outer boundary.")

    _, outer_index = min(candidates)
    outer_vertex = outer[outer_index]

    rotated_hole = hole[hole_vertex_index:] + hole[:hole_vertex_index]
    merged: list[Point2D] = []
    merged.extend(outer[: outer_index + 1])
    merged.append(hole_vertex)
    merged.extend(rotated_hole[1:])
    merged.append(hole_vertex)
    merged.append(outer_vertex)
    merged.extend(outer[outer_index + 1 :])
    return merged


def _segment_inside_domain(
    outer: list[Point2D],
    holes: list[list[Point2D]],
    start: Point2D,
    end: Point2D,
    allow_hole_endpoint: Point2D | None = None,
) -> bool:

    return segment_inside_boundaries(
        start,
        end,
        [outer, *holes],
        lambda midpoint: _domain_contains_point(outer, holes, midpoint),
        allow_boundary_endpoint=allow_hole_endpoint,
    )


def _domain_contains_point(
    outer: list[Point2D], holes: list[list[Point2D]], point: Point2D
) -> bool:
    if not Polygon(outer).contains_point(point):
        return False
    return not any(
        Polygon(hole).contains_point(point)
        and not Polygon(hole).point_on_boundary(point)
        for hole in holes
    )
