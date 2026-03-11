"""Incremental Delaunay triangulation using visibility walk, edge legalization, and spatial indexing."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Iterable

from ...kernel import (
    EPSILON,
    Point,
    contains_point,
    cross_product,
    in_circle,
)

if TYPE_CHECKING:
    from .mesh import TriangleMesh


class IncrementalTriangle:
    """A triangle in the incremental Delaunay mesh with adjacency information."""
    __slots__ = ("vertices", "neighbors")

    def __init__(self, v1: Point, v2: Point, v3: Point):
        # Ensure CCW orientation
        if cross_product(v1, v2, v3) < 0:
            self.vertices = [v1, v3, v2]
        else:
            self.vertices = [v1, v2, v3]
        # neighbors[i] is the triangle opposite to vertices[i]
        self.neighbors: list[IncrementalTriangle | None] = [None, None, None]

    def contains_point(self, point: Point) -> bool:
        """Geometric containment check using cross products."""
        for i in range(3):
            if cross_product(self.vertices[i], self.vertices[(i + 1) % 3], point) < -EPSILON:
                return False
        return True


class PointGrid:
    """Simple 2D grid for fast nearest-neighbor search."""
    def __init__(self, points: Iterable[Point]):
        pts = list(points)
        if not pts:
            self.min_x = self.max_x = self.min_y = self.max_y = 0.0
            self.grid = {}
            self.cell_size = 1.0
            self.num_cells = 1
            return

        self.min_x = min(p.x for p in pts)
        self.max_x = max(p.x for p in pts)
        self.min_y = min(p.y for p in pts)
        self.max_y = max(p.y for p in pts)
        
        n = len(pts)
        self.num_cells = int(math.sqrt(n)) + 1
        self.cell_size = max((self.max_x - self.min_x) / self.num_cells, 
                             (self.max_y - self.min_y) / self.num_cells, 
                             0.1)
        
        self.grid: dict[tuple[int, int], list[Point]] = {}

    def _get_cell(self, p: Point) -> tuple[int, int]:
        return (int((p.x - self.min_x) / self.cell_size), 
                int((p.y - self.min_y) / self.cell_size))

    def add(self, p: Point):
        cell = self._get_cell(p)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(p)

    def find_nearest(self, p: Point) -> Point | None:
        """Finds the nearest point in the grid to point p."""
        if not self.grid:
            return None
            
        cx, cy = self._get_cell(p)
        nearest = None
        min_dist_sq = float('inf')
        
        radius = 0
        while not nearest and radius < self.num_cells:
            for i in range(cx - radius, cx + radius + 1):
                for j in range(cy - radius, cy + radius + 1):
                    if abs(i - cx) != radius and abs(j - cy) != radius:
                        continue
                    cell_points = self.grid.get((i, j))
                    if cell_points:
                        for cp in cell_points:
                            dist_sq = (p.x - cp.x)**2 + (p.y - cp.y)**2
                            if dist_sq < min_dist_sq:
                                min_dist_sq = dist_sq
                                nearest = cp
            radius += 1
        return nearest


class IncrementalDelaunayMesher:
    """
    Stateful Incremental Delaunay Mesher.
    Uses spatial indexing for fast point location and visibility walks.
    """
    def __init__(self, points_for_grid: Iterable[Point] | None = None):
        self.active_triangles: set[IncrementalTriangle] = set()
        self.vertex_to_triangles: dict[Point, set[IncrementalTriangle]] = {}
        self.grid = PointGrid(points_for_grid) if points_for_grid else None
        self.super_vertices: set[Point] = set()
        self.skipped: list[tuple[Point, str]] = []
        self.root: IncrementalTriangle | None = None

    def _create_super_triangle(self, points: Iterable[Point]) -> tuple[Point, Point, Point]:
        """Creates a super-triangle that encloses all given points."""
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        dx = max_x - min_x
        dy = max_y - min_y
        delta = max(dx, dy, 1.0) * 20
        mid_x = (min_x + max_x) / 2
        
        return (
            Point(mid_x, max_y + delta, id=-1),
            Point(min_x - delta, min_y - delta, id=-2),
            Point(max_x + delta, min_y - delta, id=-3),
        )

    def _add_triangle_to_vertex_map(self, tri: IncrementalTriangle):
        for v in tri.vertices:
            if v not in self.vertex_to_triangles:
                self.vertex_to_triangles[v] = set()
            self.vertex_to_triangles[v].add(tri)

    def _remove_triangle_from_vertex_map(self, tri: IncrementalTriangle, old_vertices: list[Point]):
        for v in old_vertices:
            if v in self.vertex_to_triangles:
                self.vertex_to_triangles[v].discard(tri)

    def _visibility_walk(self, point: Point, start_tri: IncrementalTriangle) -> IncrementalTriangle | None:
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

    def _legalize_edge(self, point: Point, tri: IncrementalTriangle, edge_idx: int):
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

    def initialize(self, points: Iterable[Point]):
        """Sets up the super-triangle and initial grid."""
        pts = list(points)
        if not pts: return
        
        if not self.grid:
            self.grid = PointGrid(pts)
            
        sv = self._create_super_triangle(pts)
        self.super_vertices = set(sv)
        self.root = IncrementalTriangle(*sv)
        self.active_triangles = {self.root}
        self.vertex_to_triangles = {
            sv[0]: {self.root}, sv[1]: {self.root}, sv[2]: {self.root}
        }
        for v in sv: self.grid.add(v)

    def add_point(self, p: Point):
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

    def get_triangles(self) -> list[tuple[Point, Point, Point]]:
        """Returns the final triangles, excluding those connected to the super-triangle."""
        final = []
        for t in self.active_triangles:
            if not any(v in self.super_vertices for v in t.vertices):
                final.append(tuple(t.vertices))
        return final

    def triangulate(self, points: list[Point]) -> tuple[list[tuple[Point, Point, Point]], list[tuple[Point, str]]]:
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

        self.initialize(unique_points)
        for p in unique_points:
            self.add_point(p)

        return self.get_triangles(), skipped_initial + self.skipped


def triangulate_incremental_fast(points: list[Point]) -> tuple[list[tuple[Point, Point, Point]], list[tuple[Point, str]]]:
    """Convenience wrapper for IncrementalDelaunayMesher."""
    mesher = IncrementalDelaunayMesher()
    return mesher.triangulate(points)
