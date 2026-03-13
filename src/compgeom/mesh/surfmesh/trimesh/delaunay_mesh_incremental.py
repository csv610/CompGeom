"""Incremental Delaunay triangulation using visibility walk, edge legalization, and spatial indexing."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Iterable

from ....kernel import (
    EPSILON,
    Point2D,
    contains_point,
    cross_product,
    in_circle,
)
from .utils import PointGrid, create_super_triangle, hilbert_key


if TYPE_CHECKING:
    from .mesh import TriangleMesh


class IncrementalTriangle:
    """A triangle in the incremental Delaunay mesh with adjacency information."""
    __slots__ = ("vertices", "neighbors")

    def __init__(self, v1: Point2D, v2: Point2D, v3: Point2D):
        # Ensure CCW orientation
        if cross_product(v1, v2, v3) < 0:
            self.vertices = [v1, v3, v2]
        else:
            self.vertices = [v1, v2, v3]
        # neighbors[i] is the triangle opposite to vertices[i]
        self.neighbors: list[IncrementalTriangle | None] = [None, None, None]

    def contains_point(self, point: Point2D) -> bool:
        """Geometric containment check using cross products."""
        for i in range(3):
            if cross_product(self.vertices[i], self.vertices[(i + 1) % 3], point) < -EPSILON:
                return False
        return True


class IncrementalDelaunayMesher:
    """
    Stateful Incremental Delaunay Mesher.
    Uses spatial indexing for fast point location and visibility walks.
    """
    def __init__(self, points_for_grid: Iterable[Point2D] | None = None):
        self.active_triangles: set[IncrementalTriangle] = set()
        self.vertex_to_triangles: dict[Point2D, set[IncrementalTriangle]] = {}
        self.grid = PointGrid(points_for_grid) if points_for_grid else None
        self.super_vertices: set[Point2D] = set()
        self.skipped: list[tuple[Point2D, str]] = []
        self.root: IncrementalTriangle | None = None

    def _add_triangle_to_vertex_map(self, tri: IncrementalTriangle):
        for v in tri.vertices:
            if v not in self.vertex_to_triangles:
                self.vertex_to_triangles[v] = set()
            self.vertex_to_triangles[v].add(tri)

    def _remove_triangle_from_vertex_map(self, tri: IncrementalTriangle, old_vertices: list[Point2D]):
        for v in old_vertices:
            if v in self.vertex_to_triangles:
                self.vertex_to_triangles[v].discard(tri)

    def _visibility_walk(self, point: Point2D, start_tri: IncrementalTriangle) -> IncrementalTriangle | None:
        curr = start_tri
        visited = {curr}
        
        while True:
            found_better = False
            for i in range(3):
                v1 = curr.vertices[(i + 1) % 3]
                v2 = curr.vertices[(i + 2) % 3]
                
                if cross_product(v1, v2, point) < -EPSILON:
                    neighbor = curr.neighbors[i]
                    if neighbor and neighbor not in visited:
                        curr = neighbor
                        visited.add(curr)
                        found_better = True
                        break
            
            if not found_better:
                if curr.contains_point(point):
                    return curr
                # Fallback to check all active triangles if walk fails
                for t in self.active_triangles:
                    if t.contains_point(point):
                        return t
                return None

    def _legalize_edge(self, point: Point2D, tri: IncrementalTriangle, edge_idx: int):
        neighbor = tri.neighbors[edge_idx]
        if neighbor is None:
            return

        n_idx = -1
        for i in range(3):
            if neighbor.neighbors[i] == tri:
                n_idx = i
                break
        if n_idx == -1: return

        a = tri.vertices[(edge_idx + 1) % 3]
        b = tri.vertices[(edge_idx + 2) % 3]
        c = point
        d = neighbor.vertices[n_idx]

        if in_circle(a, b, c, d):
            n_ca = tri.neighbors[(edge_idx + 2) % 3]
            n_cb = tri.neighbors[(edge_idx + 1) % 3]
            n_db = neighbor.neighbors[(n_idx + 2) % 3]
            n_da = neighbor.neighbors[(n_idx + 1) % 3]

            old_tri_v = list(tri.vertices)
            old_neighbor_v = list(neighbor.vertices)
            self._remove_triangle_from_vertex_map(tri, old_tri_v)
            self._remove_triangle_from_vertex_map(neighbor, old_neighbor_v)

            tri.vertices = [c, a, d]
            neighbor.vertices = [c, d, b]

            tri.neighbors = [n_da, neighbor, n_ca]
            neighbor.neighbors = [n_db, n_cb, tri]

            self._add_triangle_to_vertex_map(tri)
            self._add_triangle_to_vertex_map(neighbor)

            if n_da:
                for i in range(3):
                    if n_da.vertices[(i + 1) % 3] == d and n_da.vertices[(i + 2) % 3] == a:
                        n_da.neighbors[i] = tri; break
            if n_cb:
                for i in range(3):
                    if n_cb.vertices[(i + 1) % 3] == c and n_cb.vertices[(i + 2) % 3] == b:
                        n_cb.neighbors[i] = neighbor; break
            
            self._legalize_edge(point, tri, 0)
            self._legalize_edge(point, neighbor, 0)

    def initialize(self, points: Iterable[Point2D]):
        """Sets up the super-triangle and initial grid."""
        pts = list(points)
        if not pts: return
        
        if not self.grid:
            self.grid = PointGrid(pts)
            
        sv = create_super_triangle(pts)
        self.super_vertices = set(sv)
        self.root = IncrementalTriangle(*sv)
        self.active_triangles = {self.root}
        self.vertex_to_triangles = {
            sv[0]: {self.root}, sv[1]: {self.root}, sv[2]: {self.root}
        }
        for v in sv: self.grid.add(v)

    def add_point(self, p: Point2D):
        """Adds a single point to the triangulation."""
        if not self.root:
            raise RuntimeError("Mesher not initialized. Call initialize() first.")
            
        nearest_vertex = self.grid.find_nearest(p)
        start_tri = next(iter(self.vertex_to_triangles[nearest_vertex])) if nearest_vertex in self.vertex_to_triangles else self.root
        
        target = self._visibility_walk(p, start_tri)
        if not target:
            self.skipped.append((p, "Point outside super-triangle or numerical error"))
            return
        
        v0, v1, v2 = target.vertices
        n0, n1, n2 = target.neighbors
        
        self._remove_triangle_from_vertex_map(target, list(target.vertices))
        self.active_triangles.remove(target)
        
        t0 = target
        t1 = IncrementalTriangle(p, v1, v2)
        t2 = IncrementalTriangle(p, v2, v0)
        
        t0.vertices = [p, v0, v1]
        t0.neighbors = [n2, t1, t2]
        t1.neighbors = [n0, t2, t0]
        t2.neighbors = [n1, t0, t1]
        
        if n0:
            for i in range(3):
                if n0.neighbors[i] == target: n0.neighbors[i] = t1; break
        if n1:
            for i in range(3):
                if n1.neighbors[i] == target: n1.neighbors[i] = t2; break
        
        self.active_triangles.update([t0, t1, t2])
        self._add_triangle_to_vertex_map(t0)
        self._add_triangle_to_vertex_map(t1)
        self._add_triangle_to_vertex_map(t2)
        
        self._legalize_edge(p, t0, 0)
        self._legalize_edge(p, t1, 0)
        self._legalize_edge(p, t2, 0)
        
        self.grid.add(p)

    def get_triangles(self) -> list[tuple[Point2D, Point2D, Point2D]]:
        """Returns the final triangles, excluding those connected to the super-triangle."""
        final = []
        for t in self.active_triangles:
            if not any(v in self.super_vertices for v in t.vertices):
                final.append(tuple(t.vertices))
        return final

    def triangulate(self, points: list[Point2D], spatial_sort: bool = True) -> tuple[list[tuple[Point2D, Point2D, Point2D]], list[tuple[Point2D, str]]]:
        """Performs batch triangulation of all given points."""
        if not points:
            return [], []

        unique_points = []
        seen = set()
        skipped_initial = []
        for p in points:
            key = (p.x, p.y)
            if key in seen:
                skipped_initial.append((p, "Duplicate Point"))
                continue
            seen.add(key)
            unique_points.append(p)

        if not unique_points:
            return [], skipped_initial

        # HEURISTIC: Spatial Sorting (Hilbert Curve)
        if spatial_sort and len(unique_points) > 2:
            min_x = min(p.x for p in unique_points)
            max_x = max(p.x for p in unique_points)
            min_y = min(p.y for p in unique_points)
            max_y = max(p.y for p in unique_points)
            range_x = max_x - min_x if max_x != min_x else 1.0
            range_y = max_y - min_y if max_y != min_y else 1.0
            
            N_HILBERT = 1 << 16
            def get_order(p: Point2D):
                hx = int((p.x - min_x) / range_x * (N_HILBERT - 1))
                hy = int((p.y - min_y) / range_y * (N_HILBERT - 1))
                return hilbert_key(hx, hy, N_HILBERT)

            unique_points.sort(key=get_order)

        self.initialize(unique_points)
        for p in unique_points:
            self.add_point(p)

        return self.get_triangles(), skipped_initial + self.skipped


def triangulate_incremental_fast(points: list[Point2D], spatial_sort: bool = True) -> tuple[list[tuple[Point2D, Point2D, Point2D]], list[tuple[Point2D, str]]]:
    """Convenience wrapper for IncrementalDelaunayMesher."""
    mesher = IncrementalDelaunayMesher()
    return mesher.triangulate(points, spatial_sort=spatial_sort)
