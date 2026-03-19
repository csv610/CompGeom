"""Shortest-path helpers for polygons."""

from __future__ import annotations

import heapq
from typing import Sequence

from compgeom.polygon.exceptions import PointOutsidePolygonError, PolygonPathNotFoundError
from compgeom.polygon.tolerance import EPSILON
from compgeom.kernel import Point2D, distance
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_utils import segment_inside_boundaries


def segment_inside_polygon(polygon: Polygon | Sequence[Point2D], start: Point2D, end: Point2D) -> bool:
    """Checks if a segment is entirely inside a polygon."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    return segment_inside_boundaries(
        start,
        end,
        [poly_obj],
        lambda midpoint: poly_obj.contains_point(midpoint) or poly_obj.point_on_boundary(midpoint),
    )


def shortest_path_in_polygon(
    polygon: Polygon | Sequence[Point2D], source: Point2D, target: Point2D
) -> tuple[list[Point2D], float]:
    """Finds the shortest path between two points inside a polygon."""
    poly_obj = polygon if isinstance(polygon, Polygon) else Polygon(polygon)
    if not poly_obj.contains_point(source):
        raise PointOutsidePolygonError("Source point must lie inside or on the boundary of the polygon.")
    if not poly_obj.contains_point(target):
        raise PointOutsidePolygonError("Target point must lie inside or on the boundary of the polygon.")


    nodes = [source, target, *poly_obj.vertices]
    graph: dict[int, list[tuple[int, float]]] = {index: [] for index in range(len(nodes))}
    for left in range(len(nodes)):
        for right in range(left + 1, len(nodes)):
            if not segment_inside_polygon(poly_obj, nodes[left], nodes[right]):
                continue
            weight = distance(nodes[left], nodes[right])
            graph[left].append((right, weight))
            graph[right].append((left, weight))

    distances = {0: 0.0}
    previous: dict[int, int] = {}
    queue = [(0.0, 0)]
    while queue:
        current_distance, node = heapq.heappop(queue)
        if current_distance > distances.get(node, float("inf")) + EPSILON:
            continue
        if node == 1:
            break
        for neighbor, weight in graph[node]:
            candidate = current_distance + weight
            if candidate + EPSILON < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    if 1 not in distances:
        raise PolygonPathNotFoundError("No path found inside the polygon.")

    path_indices = [1]
    while path_indices[-1] != 0:
        path_indices.append(previous[path_indices[-1]])
    path_indices.reverse()
    return [nodes[index] for index in path_indices], distances[1]


__all__ = ["segment_inside_polygon", "shortest_path_in_polygon"]
