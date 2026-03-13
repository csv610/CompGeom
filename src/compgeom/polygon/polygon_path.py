"""Shortest-path helpers for polygons."""

from __future__ import annotations

import heapq

from ..kernel import EPSILON, Point2D
from ..kernel import distance
from .polygon import Polygon
from .polygon_utils import point_on_boundary, segment_inside_boundaries


def segment_inside_polygon(polygon: list[Point2D], start: Point2D, end: Point2D) -> bool:
    polygon_shape = Polygon(polygon)
    return segment_inside_boundaries(
        start,
        end,
        [polygon],
        lambda midpoint: polygon_shape.contains_point(midpoint) or point_on_boundary(midpoint, polygon),
    )


def shortest_path_in_polygon(
    polygon: list[Point2D], source: Point2D, target: Point2D
) -> tuple[list[Point2D], float]:
    polygon_shape = Polygon(polygon)
    if not polygon_shape.contains_point(source):
        raise ValueError("Source point must lie inside or on the boundary of the polygon.")
    if not polygon_shape.contains_point(target):
        raise ValueError("Target point must lie inside or on the boundary of the polygon.")

    nodes = [source, target, *polygon]
    graph: dict[int, list[tuple[int, float]]] = {index: [] for index in range(len(nodes))}
    for left in range(len(nodes)):
        for right in range(left + 1, len(nodes)):
            if not segment_inside_polygon(polygon, nodes[left], nodes[right]):
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
        raise ValueError("No path found inside the polygon.")

    path_indices = [1]
    while path_indices[-1] != 0:
        path_indices.append(previous[path_indices[-1]])
    path_indices.reverse()
    return [nodes[index] for index in path_indices], distances[1]

__all__ = ["segment_inside_polygon", "shortest_path_in_polygon"]
