"""Art gallery problem solvers and guard placement algorithms."""

from __future__ import annotations

from collections import deque
from typing import List, Tuple

from ..geo_math.geometry import Point


class PolygonGuards:
    """Guard placement algorithms for simple polygons."""

    @staticmethod
    def guard_polygon(
        triangles: List[Tuple[int, int, int]], vertices: List[Point]
    ) -> List[Point]:
        return guard_polygon(triangles, vertices)

    @staticmethod
    def solve_art_gallery(polygon_input: List[Point]) -> List[Point]:
        return solve_art_gallery(polygon_input)


def guard_polygon(
    triangles: List[Tuple[int, int, int]], vertices: List[Point]
) -> List[Point]:
    """
    Solves the art gallery problem using Chvátal's algorithm (3-coloring of triangulation).
    
    Args:
        triangles: List of vertex index triples representing the triangulation.
        vertices: List of points corresponding to the vertex indices.
        
    Returns:
        A list of points representing the positions for the guards.
    """
    if not triangles:
        return []

    # Map vertex index to color (0, 1, or 2)
    colors = {}
    first = triangles[0]
    colors[first[0]], colors[first[1]], colors[first[2]] = 0, 1, 2

    # BFS traversal through triangles to 3-color the dual graph
    processed = [False] * len(triangles)
    processed[0] = True
    queue = deque([0])

    while queue:
        current_index = queue.popleft()
        current_triangle = triangles[current_index]
        
        # In a real triangulation graph, we would use an adjacency list for speed,
        # but for simplicity and smaller polygons, this linear search works.
        for index, triangle in enumerate(triangles):
            if processed[index]:
                continue

            shared = set(current_triangle).intersection(triangle)
            if len(shared) != 2:
                continue

            # Color the third vertex based on the two shared ones
            new_vertex = next(iter(set(triangle) - shared))
            colors[new_vertex] = 3 - sum(colors[vertex] for vertex in shared)
            processed[index] = True
            queue.append(index)

    # Collect vertices by color group
    groups: List[List[Point]] = [[], [], []]
    for vertex_index, color in colors.items():
        if vertex_index < len(vertices):
            groups[color].append(vertices[vertex_index])
            
    # Return the smallest group (Chvátal's theorem: floor(n/3) guards)
    return min(groups, key=len)


def solve_art_gallery(polygon_input: List[Point]) -> List[Point]:
    """
    Standard interface to solve the art gallery problem for a list of points.
    
    Args:
        polygon_input: A list of points forming a simple polygon.
        
    Returns:
        A list of points representing guard positions.
    """
    from .polygon_decomposer import _ear_clip

    triangles, _, vertices = _ear_clip(polygon_input)
    return guard_polygon(triangles, vertices)
