"""
Delaunay triangulation using the Incremental Edge Flip algorithm.
This implementation follows the structure of delaunay_mesh_incremental.py but uses
an explicit queue-based edge flipping mechanism for legalization.
"""

from __future__ import annotations

import math
from collections import deque
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


class EdgeFlipTriangle:
    """A triangle with adjacency information for edge flipping."""
    __slots__ = ("vertices", "neighbors")

    def __init__(self, v1: Point, v2: Point, v3: Point):
        # Ensure CCW orientation
        if cross_product(v1, v2, v3) < 0:
            self.vertices = [v1, v3, v2]
        else:
            self.vertices = [v1, v2, v3]
        # neighbors[i] is the triangle opposite to vertices[i]
        # neighbor[0] is opposite vertices[0], sharing edge (vertices[1], vertices[2])
        self.neighbors: list[EdgeFlipTriangle | None] = [None, None, None]

    def contains_point(self, point: Point) -> bool:
        """Geometric containment check using cross products."""
        for i in range(3):
            if cross_product(self.vertices[i], self.vertices[(i + 1) % 3], point) < -EPSILON:
                return False
        return True

    def get_edge_index(self, v1: Point, v2: Point) -> int:
        """Finds the index of the neighbor sharing edge (v1, v2)."""
        for i in range(3):
            va = self.vertices[(i + 1) % 3]
            vb = self.vertices[(i + 2) % 3]
            if (va == v1 and vb == v2) or (va == v2 and vb == v1):
                return i
        return -1


class PointGrid:
    """Simple 2D grid for fast nearest-neighbor search to seed visibility walks."""
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


class EdgeFlipDelaunayMesher:
    """
    Incremental Delaunay Mesher using the Edge Flip algorithm.
    Uses visibility walks for point location and a queue-based edge flipping approach.
    """
    def __init__(self, points_for_grid: Iterable[Point] | None = None):
        self.active_triangles: set[EdgeFlipTriangle] = set()
        self.vertex_to_triangles: dict[Point, set[EdgeFlipTriangle]] = {}
        self.grid = PointGrid(points_for_grid) if points_for_grid else None
        self.super_vertices: set[Point] = set()
        self.skipped: list[tuple[Point, str]] = []
        self.root: EdgeFlipTriangle | None = None

    def _create_super_triangle(self, points: Iterable[Point]) -> tuple[Point, Point, Point]:
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

    def _add_triangle(self, tri: EdgeFlipTriangle):
        self.active_triangles.add(tri)
        for v in tri.vertices:
            if v not in self.vertex_to_triangles:
                self.vertex_to_triangles[v] = set()
            self.vertex_to_triangles[v].add(tri)

    def _remove_triangle(self, tri: EdgeFlipTriangle):
        self.active_triangles.discard(tri)
        for v in tri.vertices:
            if v in self.vertex_to_triangles:
                self.vertex_to_triangles[v].discard(tri)

    def _visibility_walk(self, point: Point, start_tri: EdgeFlipTriangle) -> EdgeFlipTriangle | None:
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
                # Fallback
                for t in self.active_triangles:
                    if t.contains_point(point):
                        return t
                return None

    def _flip_edges(self, suspect_edges: deque[tuple[EdgeFlipTriangle, int]]):
        """Processes a queue of suspect edges and flips them if they are non-Delaunay."""
        while suspect_edges:
            t1, i1 = suspect_edges.popleft()
            t2 = t1.neighbors[i1]
            if t2 is None:
                continue

            # Index of t1 in t2's neighbors
            i2 = -1
            for j in range(3):
                if t2.neighbors[j] == t1:
                    i2 = j
                    break
            if i2 == -1: continue

            # Vertices of the quadrilateral
            # a, b are the common edge vertices
            # c is the vertex in t1 opposite to t2
            # d is the vertex in t2 opposite to t1
            c = t1.vertices[i1]
            a = t1.vertices[(i1 + 1) % 3]
            b = t1.vertices[(i1 + 2) % 3]
            d = t2.vertices[i2]

            # Shortest Diagonal Flip Criterion:
            # Current diagonal is (a, b), potential new diagonal is (c, d)
            # We flip if the new diagonal is shorter than the current one.
            dist_sq_current = (a.x - b.x)**2 + (a.y - b.y)**2
            dist_sq_new = (c.x - d.x)**2 + (c.y - d.y)**2

            if dist_sq_new < dist_sq_current:
                # Flip the edge (a, b) to (c, d)
                n_ac = t1.neighbors[(i1 + 2) % 3]
                n_bc = t1.neighbors[(i1 + 1) % 3]
                n_bd = t2.neighbors[(i2 + 2) % 3]
                n_ad = t2.neighbors[(i2 + 1) % 3]

                # Update vertices and neighbors for the two triangles
                # We update in-place to keep references valid in the queue if possible,
                # but it's safer to just be careful.
                
                self._remove_triangle(t1)
                self._remove_triangle(t2)

                t1.vertices = [c, a, d]
                t2.vertices = [c, d, b]

                t1.neighbors = [n_ad, t2, n_ac]
                t2.neighbors = [n_bd, n_bc, t1]

                self._add_triangle(t1)
                self._add_triangle(t2)

                # Update the external neighbors that now point to the flipped triangles
                if n_ad:
                    idx = n_ad.get_edge_index(a, d)
                    if idx != -1: n_ad.neighbors[idx] = t1
                if n_bc:
                    idx = n_bc.get_edge_index(b, c)
                    if idx != -1: n_bc.neighbors[idx] = t2
                # n_ac and n_bd already point to t1 and t2 respectively via their old configuration
                # but their edge indices might have changed. Actually, they stay pointing to the same tri object.

                # Add new suspect edges to the queue
                suspect_edges.append((t1, 0)) # edge (a, d)
                suspect_edges.append((t1, 2)) # edge (c, a)
                suspect_edges.append((t2, 0)) # edge (d, b)
                suspect_edges.append((t2, 1)) # edge (c, b)

    def initialize(self, points: Iterable[Point]):
        pts = list(points)
        if not pts: return
        
        if not self.grid:
            self.grid = PointGrid(pts)
            
        sv = self._create_super_triangle(pts)
        self.super_vertices = set(sv)
        self.root = EdgeFlipTriangle(*sv)
        self._add_triangle(self.root)
        for v in sv: self.grid.add(v)

    def add_point(self, p: Point):
        if not self.root:
            raise RuntimeError("Mesher not initialized.")
            
        nearest_vertex = self.grid.find_nearest(p)
        start_tri = next(iter(self.vertex_to_triangles[nearest_vertex])) if nearest_vertex in self.vertex_to_triangles else self.root
        
        target = self._visibility_walk(p, start_tri)
        if not target:
            self.skipped.append((p, "Point outside super-triangle"))
            return
        
        v0, v1, v2 = target.vertices
        n0, n1, n2 = target.neighbors
        
        self._remove_triangle(target)
        
        # Split target into 3 triangles: (p, v0, v1), (p, v1, v2), (p, v2, v0)
        t0 = target # Reuse the object
        t1 = EdgeFlipTriangle(p, v1, v2)
        t2 = EdgeFlipTriangle(p, v2, v0)
        
        t0.vertices = [p, v0, v1]
        t0.neighbors = [n2, t1, t2]
        t1.neighbors = [n0, t2, t0]
        t2.neighbors = [n1, t0, t1]
        
        if n0:
            idx = n0.get_edge_index(v1, v2)
            if idx != -1: n0.neighbors[idx] = t1
        if n1:
            idx = n1.get_edge_index(v2, v0)
            if idx != -1: n1.neighbors[idx] = t2
        if n2:
            # n2 already points to target (which is t0), but we update for clarity
            idx = n2.get_edge_index(v0, v1)
            if idx != -1: n2.neighbors[idx] = t0

        self._add_triangle(t0)
        self._add_triangle(t1)
        self._add_triangle(t2)
        
        # Suspect edges are the outer edges of the original triangle AND the 3 new internal edges.
        # Outer edges: (t0, 0), (t1, 0), (t2, 0)
        # Internal edges: (t0, 1), (t1, 1), (t2, 1) - each shared between two of the new triangles
        suspects = deque([(t0, 0), (t1, 0), (t2, 0), (t0, 1), (t1, 1), (t2, 1)])
        self._flip_edges(suspects)
        
        self.grid.add(p)

    def get_triangles(self) -> list[tuple[Point, Point, Point]]:
        return [tuple(t.vertices) for t in self.active_triangles 
                if not any(v in self.super_vertices for v in t.vertices)]

    def triangulate(self, points: list[Point]) -> tuple[list[tuple[Point, Point, Point]], list[tuple[Point, str]]]:
        if not points: return [], []
        
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

        if not unique_points: return [], skipped_initial

        self.initialize(unique_points)
        for p in unique_points:
            self.add_point(p)

        return self.get_triangles(), skipped_initial + self.skipped


def triangulate_edgeflip(points: list[Point]) -> tuple[list[tuple[Point, Point, Point]], list[tuple[Point, str]]]:
    """Convenience wrapper for EdgeFlipDelaunayMesher."""
    mesher = EdgeFlipDelaunayMesher()
    return mesher.triangulate(points)
