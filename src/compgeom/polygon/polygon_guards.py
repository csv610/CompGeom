"""Art gallery problem solvers and guard placement algorithms."""

from __future__ import annotations

from collections import deque
from typing import List, Tuple, Sequence

from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_decomposer import triangulate_polygon


def art_gallery_guards(polygon: Polygon | Sequence[Point2D]) -> List[Point2D]:
    """
    Solves the art gallery problem for a simple polygon.
    """
    poly_list = polygon.as_list() if isinstance(polygon, Polygon) else list(polygon)
    triangles, _, vertices = triangulate_polygon(poly_list)
    return guard_polygon(triangles, vertices)


def guard_polygon(
    triangles: List[Tuple[int, int, int]], vertices: List[Point2D]
) -> List[Point2D]:
    """
    Solves the art gallery problem using Chvátal's algorithm (3-coloring of triangulation).
    """
    if not triangles:
        return []

    colors = {}
    first = triangles[0]
    colors[first[0]], colors[first[1]], colors[first[2]] = 0, 1, 2

    processed = [False] * len(triangles)
    processed[0] = True
    queue = deque([0])

    while queue:
        current_index = queue.popleft()
        current_triangle = triangles[current_index]
        
        for index, triangle in enumerate(triangles):
            if processed[index]:
                continue

            shared = set(current_triangle).intersection(triangle)
            if len(shared) != 2:
                continue

            new_vertex = next(iter(set(triangle) - shared))
            colors[new_vertex] = 3 - sum(colors[vertex] for vertex in shared)
            processed[index] = True
            queue.append(index)

    groups: List[List[Point2D]] = [[], [], []]
    for vertex_index, color in colors.items():
        if vertex_index < len(vertices):
            groups[color].append(vertices[vertex_index])
            
    return min(groups, key=len)


__all__ = ["art_gallery_guards", "guard_polygon"]
