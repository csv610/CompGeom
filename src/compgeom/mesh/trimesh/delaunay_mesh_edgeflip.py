"""
Delaunay triangulation using the Incremental Edge Flip algorithm.
This implementation follows the structure of delaunay_mesh_incremental.py but uses
an explicit stack-based edge flipping mechanism for legalization.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Iterable

from ...kernel import (
    EPSILON,
    Point,
    contains_point,
    cross_product,
    in_circle,
    incircle_sign,
    robust_orientation,
    robust_in_circle,
)
from .utils import PointGrid, create_super_triangle, hilbert_key


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
        # neighbor[i] shares edge (vertices[(i+1)%3], vertices[(i+2)%3])
        self.neighbors: list[EdgeFlipTriangle | None] = [None, None, None]

    def contains_point(self, point: Point) -> bool:
        """Geometric containment check using cross products."""
        # Use a consistent epsilon for containment robustness
        for i in range(3):
            if cross_product(self.vertices[i], self.vertices[(i + 1) % 3], point) < -1e-11:
                return False
        return True

    def get_edge_index(self, v1: Point, v2: Point) -> int:
        """Finds the index i such that neighbors[i] is the triangle sharing edge (v1, v2)."""
        for i in range(3):
            va = self.vertices[(i + 1) % 3]
            vb = self.vertices[(i + 2) % 3]
            if (va == v1 and vb == v2) or (va == v2 and vb == v1):
                return i
        return -1


class EdgeFlipDelaunayMesher:
    """
    Incremental Delaunay Mesher using the Edge Flip algorithm.
    Optimized for numerical robustness and triangle reuse.
    """
    def __init__(self, points_for_grid: Iterable[Point] | None = None):
        self.active_triangles: set[EdgeFlipTriangle] = set()
        self.vertex_to_triangles: dict[Point, set[EdgeFlipTriangle]] = {}
        self.grid = PointGrid(points_for_grid) if points_for_grid else None
        self.super_vertices: set[Point] = set()
        self.skipped: list[tuple[Point, str]] = []
        self.root: EdgeFlipTriangle | None = None
        self.last_tri: EdgeFlipTriangle | None = None

    def _add_triangle(self, tri: EdgeFlipTriangle):
        self.active_triangles.add(tri)
        self.last_tri = tri
        for v in tri.vertices:
            if v not in self.vertex_to_triangles:
                self.vertex_to_triangles[v] = set()
            self.vertex_to_triangles[v].add(tri)

    def _remove_triangle(self, tri: EdgeFlipTriangle):
        if tri in self.active_triangles:
            self.active_triangles.remove(tri)
        if self.last_tri == tri:
            self.last_tri = None
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
                
                if robust_orientation(v1, v2, point) < -1e-10:
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

    def _update_neighbor(self, neighbor: EdgeFlipTriangle | None, v1: Point, v2: Point, new_tri: EdgeFlipTriangle):
        """Updates neighbor's adjacency pointer if it shares the edge (v1, v2)."""
        if neighbor:
            idx = neighbor.get_edge_index(v1, v2)
            if idx != -1:
                neighbor.neighbors[idx] = new_tri

    def _flip_edges(self, suspect_edges: list[tuple[EdgeFlipTriangle, int]]):
        """Processes a stack of suspect edges and flips them if they are non-Delaunay."""
        while suspect_edges:
            t1, i1 = suspect_edges.pop()
            if t1 not in self.active_triangles:
                continue
            
            t2 = t1.neighbors[i1]
            if not t2: continue

            i2 = t2.get_edge_index(t1.vertices[(i1+1)%3], t1.vertices[(i1+2)%3])
            if i2 == -1: continue

            c, a, b = t1.vertices[i1], t1.vertices[(i1+1)%3], t1.vertices[(i1+2)%3]
            d = t2.vertices[i2]

            if robust_in_circle(a, b, c, d):
                n_ac = t1.neighbors[(i1 + 2) % 3]
                n_cb = t1.neighbors[(i1 + 1) % 3]
                n_bd = t2.neighbors[(i2 + 2) % 3]
                n_da = t2.neighbors[(i2 + 1) % 3]

                # Triangle Reuse: update in-place
                self._remove_triangle(t1)
                self._remove_triangle(t2)

                t1.vertices = [c, a, d]
                t1.neighbors = [n_da, t2, n_ac]
                t2.vertices = [c, d, b]
                t2.neighbors = [n_bd, n_cb, t1]

                self._add_triangle(t1)
                self._add_triangle(t2)

                self._update_neighbor(n_da, a, d, t1)
                self._update_neighbor(n_ac, c, a, t1)
                self._update_neighbor(n_bd, d, b, t2)
                self._update_neighbor(n_cb, b, c, t2)

                suspect_edges.extend([(t1, 0), (t1, 2), (t2, 0), (t2, 1)])

    def initialize(self, points: Iterable[Point]):
        pts = list(points)
        if not pts: return
        
        if not self.grid:
            self.grid = PointGrid(pts)
            
        sv = create_super_triangle(pts)
        self.super_vertices = set(sv)
        self.root = EdgeFlipTriangle(*sv)
        self._add_triangle(self.root)
        
        # Ensure super-vertices are in the grid to seed walks if necessary
        for v in sv: self.grid.add(v)

    def _split_triangle(self, p: Point, target: EdgeFlipTriangle):
        """Splits a triangle into three by inserting a point inside."""
        v0, v1, v2 = target.vertices
        n0, n1, n2 = target.neighbors 
        
        self._remove_triangle(target)
        
        t0 = EdgeFlipTriangle(p, v1, v2)
        t1 = EdgeFlipTriangle(p, v2, v0)
        t2 = EdgeFlipTriangle(p, v0, v1)
        
        t0.neighbors = [n0, t1, t2]
        t1.neighbors = [n1, t2, t0]
        t2.neighbors = [n2, t0, t1]
        
        self._update_neighbor(n0, v1, v2, t0)
        self._update_neighbor(n1, v2, v0, t1)
        self._update_neighbor(n2, v0, v1, t2)

        self._add_triangle(t0)
        self._add_triangle(t1)
        self._add_triangle(t2)
        
        return t0, t1, t2

    def add_point(self, p: Point):
        if not self.root:
            raise RuntimeError("Mesher not initialized.")
            
        # Optimization: seed walk from last triangle or nearest grid vertex
        start_tri = self.last_tri or self.root
        
        target = self._visibility_walk(p, start_tri)
        if not target:
            # Fallback to the grid if the 'nearby' heuristic fails
            if self.grid:
                nearest_vertex = self.grid.find_nearest(p)
                if nearest_vertex in self.vertex_to_triangles and self.vertex_to_triangles[nearest_vertex]:
                    start_tri = next(iter(self.vertex_to_triangles[nearest_vertex]))
                    target = self._visibility_walk(p, start_tri)
            else:
                # Last resort fallback: check all triangles
                for t in self.active_triangles:
                    if t.contains_point(p):
                        target = t
                        break

        if not target:
            self.skipped.append((p, "Point outside super-triangle"))
            return
        
        t0, t1, t2 = self._split_triangle(p, target)
        
        # Legalize using a Stack (LIFO) for better cache locality
        suspects = [(t0, 0), (t1, 0), (t2, 0), (t0, 1), (t1, 1), (t2, 1)]
        self._flip_edges(suspects)
        
        if self.grid:
            self.grid.add(p)

    def get_triangles(self) -> list[tuple[Point, Point, Point]]:
        return [tuple(t.vertices) for t in self.active_triangles 
                if not any(v in self.super_vertices for v in t.vertices)]

    def initialize_from_mesh(self, mesh: TriangleMesh):
        """Seeds the mesher with an existing TriangleMesh to avoid starting from scratch."""
        self.active_triangles = set()
        self.vertex_to_triangles = {}
        
        # 1. Create EdgeFlipTriangle objects
        tri_list = []
        for face in mesh.faces:
            v1, v2, v3 = [mesh.vertices[i] for i in face]
            tri = EdgeFlipTriangle(v1, v2, v3)
            tri_list.append(tri)
            self._add_triangle(tri)
            
        # 2. Reconstruct neighbors (adjacency)
        # This is O(F) using a edge-to-triangle map
        edge_to_tri = {}
        for tri in tri_list:
            for i in range(3):
                v_start = tri.vertices[(i + 1) % 3]
                v_end = tri.vertices[(i + 2) % 3]
                edge = tuple(sorted((v_start.id, v_end.id)))
                if edge in edge_to_tri:
                    other_tri, other_idx = edge_to_tri[edge]
                    tri.neighbors[i] = other_tri
                    other_tri.neighbors[other_idx] = tri
                else:
                    edge_to_tri[edge] = (tri, i)
        
        # 3. Add to grid for point location
        if not self.grid:
            self.grid = PointGrid(mesh.vertices)
        for v in mesh.vertices:
            self.grid.add(v)
            
        # Note: This mesh doesn't have a super-triangle. 
        self.root = tri_list[0] if tri_list else None

    def triangulate(self, points: list[Point], existing_mesh: TriangleMesh | None = None, spatial_sort: bool = True) -> tuple[list[tuple[Point, Point, Point]], list[tuple[Point, str]]]:
        if not points and not existing_mesh: return [], []
        
        unique_points = []
        seen = set()
        skipped_initial = []
        
        if existing_mesh:
            for v in existing_mesh.vertices:
                seen.add((v.x, v.y))

        for p in points:
            key = (p.x, p.y)
            if key in seen:
                skipped_initial.append((p, "Duplicate Point"))
                continue
            seen.add(key)
            unique_points.append(p)

        if not unique_points and not existing_mesh:
            return [], skipped_initial

        # HEURISTIC: Spatial Sorting (Hilbert Curve)
        if spatial_sort and unique_points:
            min_x = min(p.x for p in unique_points)
            max_x = max(p.x for p in unique_points)
            min_y = min(p.y for p in unique_points)
            max_y = max(p.y for p in unique_points)
            range_x = max_x - min_x if max_x != min_x else 1.0
            range_y = max_y - min_y if max_y != min_y else 1.0
            
            # Grid size for Hilbert: 2^16 resolution
            N_HILBERT = 1 << 16
            def get_order(p: Point):
                hx = int((p.x - min_x) / range_x * (N_HILBERT - 1))
                hy = int((p.y - min_y) / range_y * (N_HILBERT - 1))
                return hilbert_key(hx, hy, N_HILBERT)

            unique_points.sort(key=get_order)

        if existing_mesh:
            self.initialize_from_mesh(existing_mesh)
        else:
            self.grid = PointGrid(unique_points)
            self.initialize(unique_points)

        for p in unique_points:
            self.add_point(p)

        return self.get_triangles(), skipped_initial + self.skipped


def triangulate_edgeflip(points: list[Point], spatial_sort: bool = True) -> tuple[list[tuple[Point, Point, Point]], list[tuple[Point, str]]]:
    """Convenience wrapper for EdgeFlipDelaunayMesher."""
    mesher = EdgeFlipDelaunayMesher()
    return mesher.triangulate(points, spatial_sort=spatial_sort)
