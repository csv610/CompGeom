"""Naive and Flip-based Delaunay Triangulation."""

from __future__ import annotations
import math
from ...kernel import Point, contains_point, cross_product


class Triangle:
    """A basic triangle class for point location."""
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = (v1, v2, v3)
        self.children: list[Triangle] = []
        self.is_active = True

    def find_leaves_containing(self, point: Point, found_leaves: set[Triangle]):
        if not contains_point(self, point):
            return
        if not self.children:
            if self.is_active:
                found_leaves.add(self)
            return
        for child in self.children:
            child.find_leaves_containing(point, found_leaves)


def _create_super_triangle(points: list[Point]) -> tuple[Point, Point, Point]:
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)
    delta = max(max_x - min_x, max_y - min_y, 1.0) * 10
    mid_x = (min_x + max_x) / 2
    return (
        Point(mid_x, max_y + delta, id=-1),
        Point(min_x - delta, min_y - delta, id=-2),
        Point(max_x + delta, min_y - delta, id=-3),
    )


def triangulate_naive(points: list[Point]):
    """Creates a naive triangulation by iteratively splitting triangles."""
    if not points:
        return [], [], set()

    super_triangle = _create_super_triangle(points)
    super_triangle_vertices = set(super_triangle)
    skipped_points = []
    existing_points = set()

    # Build spatial index helpers to speed up point-location.
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)
    span = max(max_x - min_x, max_y - min_y, 1.0)
    cell_size = span / max(math.sqrt(max(1, len(points))), 1.0)

    class _IndexedTriangle:
        def __init__(self, vertices: tuple[Point, Point, Point]):
            self.vertices = vertices
            self.min_x = min(v.x for v in vertices)
            self.max_x = max(v.x for v in vertices)
            self.min_y = min(v.y for v in vertices)
            self.max_y = max(v.y for v in vertices)
            self.cells: list[tuple[int, int]] = []

    class _TriangleSpatialIndex:
        def __init__(self, cell_size: float):
            self.cell_size = cell_size
            self.grid: dict[tuple[int, int], list[_IndexedTriangle]] = {}

        def _cell_coords(self, x: float, y: float) -> tuple[int, int]:
            ix = int(math.floor((x - min_x) / self.cell_size))
            iy = int(math.floor((y - min_y) / self.cell_size))
            return ix, iy

        def _cells_for_bbox(self, tri: _IndexedTriangle):
            min_ix, min_iy = self._cell_coords(tri.min_x, tri.min_y)
            max_ix, max_iy = self._cell_coords(tri.max_x, tri.max_y)
            for ix in range(min_ix, max_ix + 1):
                for iy in range(min_iy, max_iy + 1):
                    yield (ix, iy)

        def add(self, tri: _IndexedTriangle):
            tri.cells = []
            for cell in self._cells_for_bbox(tri):
                self.grid.setdefault(cell, []).append(tri)
                tri.cells.append(cell)

        def remove(self, tri: _IndexedTriangle):
            for cell in tri.cells:
                cell_list = self.grid.get(cell)
                if not cell_list:
                    continue
                try:
                    cell_list.remove(tri)
                except ValueError:
                    continue
                if not cell_list:
                    del self.grid[cell]
            tri.cells = []

        def query(self, point: Point):
            ix, iy = self._cell_coords(point.x, point.y)
            seen = set()
            candidates = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    cell = (ix + dx, iy + dy)
                    for tri in self.grid.get(cell, []):
                        if tri in seen:
                            continue
                        seen.add(tri)
                        candidates.append(tri)
            return candidates

    spatial_index = _TriangleSpatialIndex(cell_size or 1.0)
    triangles_list: list[_IndexedTriangle] = []

    def make_ccw(a: Point, b: Point, c: Point):
        return (a, b, c) if cross_product(a, b, c) >= 0 else (a, c, b)

    def add_triangle(vertices: tuple[Point, Point, Point]):
        entry = _IndexedTriangle(vertices)
        triangles_list.append(entry)
        spatial_index.add(entry)
        return entry

    add_triangle(super_triangle)

    for point in points:
        if point in existing_points or any(point == vertex for vertex in super_triangle_vertices):
            skipped_points.append((point, "Duplicate/Coincident Point"))
            continue

        candidates = spatial_index.query(point)
        containing_entry = None
        for entry in candidates:
            if contains_point(Triangle(*entry.vertices), point):
                containing_entry = entry
                break

        if not containing_entry:
            for entry in triangles_list:
                if contains_point(Triangle(*entry.vertices), point):
                    containing_entry = entry
                    break

        if not containing_entry:
            skipped_points.append((point, "Outside super-triangle (Numerical Error)"))
            continue

        spatial_index.remove(containing_entry)
        triangles_list.remove(containing_entry)
        a, b, c = containing_entry.vertices
        add_triangle(make_ccw(a, b, point))
        add_triangle(make_ccw(b, c, point))
        add_triangle(make_ccw(c, a, point))

        existing_points.add(point)

    return [entry.vertices for entry in triangles_list], skipped_points, super_triangle_vertices
