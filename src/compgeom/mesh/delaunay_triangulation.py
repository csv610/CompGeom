"""Delaunay triangulation algorithms (standard, dynamic, divide and conquer, and constrained)."""

from __future__ import annotations

import math
from collections import deque

from ..geo_math.geometry import (
    EPSILON,
    Point,
    contains_point,
    cross_product,
    incircle_sign,
    in_circle,
    is_on_segment,
    orientation_sign,
    sub,
)


from .delaunay_mesh_incremental import triangulate_incremental_fast


def _get_angle(p1: Point, p2: Point) -> float:
    return math.atan2(p2.y - p1.y, p2.x - p1.x)


def triangulate_divide_and_conquer(points: list[Point]):
    """Delaunay Triangulation using the Divide and Conquer algorithm."""
    if not points:
        return [], []
    
    # Sort points and remove duplicates
    sorted_points = sorted(points, key=lambda p: (p.x, p.y))
    unique_points = []
    skipped = []
    for p in sorted_points:
        if unique_points and p.x == unique_points[-1].x and p.y == unique_points[-1].y:
            skipped.append((p, "Duplicate Point"))
            continue
        unique_points.append(p)
    
    if len(unique_points) < 2:
        return [], skipped

    adj = _dc_triangulate(unique_points)
    
    # Convert adjacency list to unique triangles
    triangles = []
    seen = set()
    for u in unique_points:
        if u not in adj: continue
        for v in adj[u]:
            if v not in adj: continue
            for w in adj[v]:
                if w not in adj: continue
                if w in adj[u]:
                    tri_key = tuple(sorted((u.id, v.id, w.id)))
                    if tri_key not in seen:
                        # Ensure CCW orientation for consistency
                        if orientation_sign(u, v, w) > 0:
                            triangles.append((u, v, w))
                        elif orientation_sign(u, v, w) < 0:
                            triangles.append((u, w, v))
                        seen.add(tri_key)
    
    return triangles, skipped


def _dc_triangulate(points: list[Point]) -> dict[Point, list[Point]]:
    n = len(points)
    if n <= 3:
        adj = {p: [] for p in points}
        if n == 2:
            u, v = points
            adj[u].append(v)
            adj[v].append(u)
        elif n == 3:
            u, v, w = points
            orient = orientation_sign(u, v, w)
            if orient == 0:
                # Collinear: connect consecutive points only
                adj[u].append(v)
                adj[v].extend([u, w])
                adj[w].append(v)
            else:
                adj[u].extend([v, w])
                adj[v].extend([u, w])
                adj[w].extend([u, v])
        for p in adj:
            adj[p].sort(key=lambda neighbor: _get_angle(p, neighbor))
        return adj

    mid = n // 2
    left_adj = _dc_triangulate(points[:mid])
    right_adj = _dc_triangulate(points[mid:])
    
    # Combined adjacency dictionary
    adj = {**left_adj, **right_adj}

    # 1. Find the base LR edge (lowest common tangent)
    # Start with rightmost of left set and leftmost of right set
    ld = points[mid - 1]
    rd = points[mid]
    
    while True:
        changed = False
        # Move ld down (CW) relative to rd
        for neighbor in adj[ld]:
            if orientation_sign(rd, ld, neighbor) < 0:
                ld = neighbor
                changed = True
                break
        if changed: continue
        
        # Move rd down (CCW) relative to ld
        for neighbor in adj[rd]:
            if orientation_sign(ld, rd, neighbor) > 0:
                rd = neighbor
                changed = True
                break
        if not changed:
            break

    # 2. Merge step: move up from the base edge
    while True:
        # Add the current LR edge to the triangulation
        if rd not in adj[ld]: adj[ld].append(rd)
        if ld not in adj[rd]: adj[rd].append(ld)
        
        # Maintain CCW sorting of neighbors
        adj[ld].sort(key=lambda neighbor: _get_angle(ld, neighbor))
        adj[rd].sort(key=lambda neighbor: _get_angle(rd, neighbor))

        # Find potential candidates for the next LR edge
        lc = None
        idx_rd = adj[ld].index(rd)
        # Check candidates on the left side in CCW order from rd
        for i in range(1, len(adj[ld])):
            cand = adj[ld][(idx_rd + i) % len(adj[ld])]
            if orientation_sign(ld, rd, cand) > 0:
                lc = cand
                # Validate lc using Delaunay criteria (in-circle test)
                while True:
                    next_idx = (adj[ld].index(lc) + 1) % len(adj[ld])
                    next_cand = adj[ld][next_idx]
                    if next_cand != rd and orientation_sign(ld, rd, next_cand) > 0 and \
                       in_circle(ld, rd, lc, next_cand):
                        # Invalidate current lc and try next neighbor
                        adj[ld].remove(lc)
                        adj[lc].remove(ld)
                        lc = next_cand
                    else:
                        break
                break
        
        rc = None
        idx_ld = adj[rd].index(ld)
        # Check candidates on the right side in CW order from ld
        for i in range(1, len(adj[rd])):
            cand = adj[rd][(idx_ld - i + len(adj[rd])) % len(adj[rd])]
            if orientation_sign(rd, ld, cand) < 0:
                rc = cand
                # Validate rc using Delaunay criteria
                while True:
                    next_idx = (adj[rd].index(rc) - 1 + len(adj[rd])) % len(adj[rd])
                    next_cand = adj[rd][next_idx]
                    if next_cand != ld and orientation_sign(rd, ld, next_cand) < 0 and \
                       in_circle(rd, ld, rc, next_cand):
                        adj[rd].remove(rc)
                        adj[rc].remove(rd)
                        rc = next_cand
                    else:
                        break
                break

        # Termination: no more candidates above the current LR edge
        if not lc and not rc:
            break
        
        # Select the next base LR edge
        if not lc or (rc and in_circle(ld, rd, lc, rc)):
            rd = rc
        else:
            ld = lc

    return adj



class DelaunayMesher:
    """
    A unified interface for Delaunay triangulation algorithms and utilities.
    
    Provides methods for incremental, divide and conquer, flip-based,
    dynamic, and constrained Delaunay triangulation.
    """

    @staticmethod
    def _to_triangle_mesh(triangles: list[tuple[Point, Point, Point]], skipped_points: list[tuple[Point, str]] | None = None) -> "TriangleMesh":
        """Converts a list of Point triangles to a TriangleMesh object."""
        from .mesh import TriangleMesh
        
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        faces = []
        for tri in triangles:
            faces.append((point_to_idx[tri[0]], point_to_idx[tri[1]], point_to_idx[tri[2]]))
            
        return TriangleMesh(unique_points, faces, skipped_points=skipped_points)

    @staticmethod
    def triangulate(points: list[Point], algorithm: str = "incremental") -> "TriangleMesh":
        """
        Performs Delaunay triangulation using the specified algorithm.
        
        Args:
            points: List of points to triangulate.
            algorithm: The algorithm to use ("incremental", "divide_and_conquer", or "flip").
            
        Returns:
            A TriangleMesh object.
        """
        skipped = []
        if algorithm == "incremental":
            triangles, skipped = triangulate_incremental_fast(points)
        elif algorithm == "divide_and_conquer":
            triangles, skipped = triangulate_divide_and_conquer(points)
        elif algorithm == "flip":
            raw_triangles, skipped, super_triangle_vertices = triangulate_naive(points)
            mesh = build_topology(raw_triangles)
            DelaunayMesher.delaunay_flip(mesh)
            triangles = [
                tuple(m.vertices) for m in mesh 
                if not any(vertex in super_triangle_vertices for vertex in m.vertices)
            ]
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
            
        return DelaunayMesher._to_triangle_mesh(triangles, skipped_points=skipped)

    @staticmethod
    def constrained_triangulate(outer_boundary: list[Point], holes: list[list[Point]] | None = None) -> "TriangleMesh":
        """Performs Constrained Delaunay Triangulation."""
        triangles, _ = constrained_delaunay_triangulation(outer_boundary, holes)
        return DelaunayMesher._to_triangle_mesh(triangles)

    @staticmethod
    def dynamic_triangulate(width: float = 1000, height: float = 1000) -> DynamicDelaunay:
        """Returns a DynamicDelaunay object for incremental point insertion."""
        return DynamicDelaunay(width, height)

    @staticmethod
    def build_mesh_topology(triangles: list[tuple[Point, Point, Point]]) -> list[MeshTriangle]:
        """Builds a mesh with neighborhood information from a list of triangles."""
        return build_topology(triangles)

    @staticmethod
    def delaunay_flip(mesh: list[MeshTriangle]):
        """Improves a triangulation by performing edge flips until it is Delaunay."""
        queue = deque()

        def edge_key(u: Point, v: Point):
            return tuple(sorted((u.id, v.id)))

        def build_triangle(vertices: tuple[Point, Point, Point], neighbors_by_edge):
            v0, v1, v2 = _make_ccw_triangle(*vertices)
            ordered_vertices = [v0, v1, v2]
            ordered_neighbors = [
                neighbors_by_edge[edge_key(v1, v2)],
                neighbors_by_edge[edge_key(v2, v0)],
                neighbors_by_edge[edge_key(v0, v1)],
            ]
            return ordered_vertices, ordered_neighbors

        def add_to_queue(triangle, index):
            if triangle.neighbors[index] is not None:
                queue.append((triangle, index))

        for triangle in mesh:
            for i in range(3):
                add_to_queue(triangle, i)

        # Optimization: Use a pass marker to track when a full cycle of the queue
        # has been completed. If no flips occur in a full cycle, the algorithm
        # terminates, even if some edges were re-queued (e.g., concave edges).
        queue.append(None)
        flips_this_pass = 0

        while queue:
            item = queue.popleft()
            if item is None:
                if flips_this_pass == 0:
                    break
                flips_this_pass = 0
                queue.append(None)
                continue

            t1, i1 = item
            t2 = t1.neighbors[i1]
            if t2 is None:
                continue

            i2 = t2.find_neighbor_index(t1)
            if i2 == -1:
                continue

            a = t1.vertices[i1]
            b = t1.vertices[(i1 + 1) % 3]
            c = t1.vertices[(i1 + 2) % 3]
            d = t2.vertices[i2]

            # Convexity check: a quadrilateral is convex if and only if both
            # diagonals intersect. This means a and d must be on opposite sides
            # of bc, AND b and c must be on opposite sides of ad.
            if orientation_sign(a, d, b) * orientation_sign(a, d, c) >= 0 or \
               orientation_sign(b, c, a) * orientation_sign(b, c, d) >= 0:
                continue

            # Use Delaunay criterion: flip if d is inside the circumcircle of abc
            if not in_circle(a, b, c, d):
                continue

            # A flip will occur
            flips_this_pass += 1
            
            # Neighbors of t1 and t2 (excluding each other)
            # t1.neighbors[i1] is t2
            n_ab = t1.neighbors[(i1 + 2) % 3] # opposite c
            n_ca = t1.neighbors[(i1 + 1) % 3] # opposite b
            
            # t2.neighbors[i2] is t1
            n_bd = t2.neighbors[(i2 + 1) % 3] # opposite c (in t2)
            n_dc = t2.neighbors[(i2 + 2) % 3] # opposite b (in t2)

            # Reassign vertices and neighbors using the new diagonal ad.
            t1.vertices, t1.neighbors = build_triangle(
                (a, b, d),
                {
                    edge_key(b, d): n_bd,
                    edge_key(d, a): t2,
                    edge_key(a, b): n_ab,
                },
            )
            t2.vertices, t2.neighbors = build_triangle(
                (a, d, c),
                {
                    edge_key(d, c): n_dc,
                    edge_key(c, a): n_ca,
                    edge_key(a, d): t1,
                },
            )

            # Update external neighbors' references to t1 and t2
            if n_bd:
                # n_bd used to point to t2, now points to t1
                idx = n_bd.find_neighbor_index(t2)
                if idx != -1: n_bd.neighbors[idx] = t1
            
            if n_ca:
                # n_ca used to point to t1, now points to t2
                idx = n_ca.find_neighbor_index(t1)
                if idx != -1: n_ca.neighbors[idx] = t2
            
            # n_ab still points to t1, n_dc still points to t2 - no change needed for them

            # Optimization: All five edges of the two new triangles (the 4 boundary 
            # edges and the new diagonal) are pushed back to the queue to be re-checked.
            for t, idx in [(t1, 0), (t1, 1), (t1, 2), (t2, 0), (t2, 1), (t2, 2)]:
                add_to_queue(t, idx)

    @staticmethod
    def improve_by_flipping(mesh: list[MeshTriangle]):
        """Improves a triangulation by performing edge flips until it is Delaunay."""
        DelaunayMesher.delaunay_flip(mesh)

    @staticmethod
    def check_is_delaunay(mesh: list[MeshTriangle]) -> bool:
        """Checks if the given mesh satisfies the Delaunay property."""
        return is_delaunay(mesh)

    @staticmethod
    def find_bad_triangles(mesh: list[MeshTriangle]) -> set[MeshTriangle]:
        """Returns the set of triangles that violate the Delaunay property."""
        return get_nondelaunay_triangles(mesh)


def triangulate(points: list[Point], algorithm: str = "incremental") -> "TriangleMesh":
    """Standalone shortcut for DelaunayMesher.triangulate."""
    return DelaunayMesher.triangulate(points, algorithm)


class Triangle:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = (v1, v2, v3)
        self.children: list["Triangle"] = []
        self.is_active = True

    def find_leaves_containing(self, point: Point, found_leaves: set["Triangle"]):
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
        return [], []

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
    triangles: list[_IndexedTriangle] = []

    def make_ccw(a: Point, b: Point, c: Point):
        return (a, b, c) if cross_product(a, b, c) >= 0 else (a, c, b)

    def add_triangle(vertices: tuple[Point, Point, Point]):
        entry = _IndexedTriangle(vertices)
        triangles.append(entry)
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
            for entry in triangles:
                if contains_point(Triangle(*entry.vertices), point):
                    containing_entry = entry
                    break

        if not containing_entry:
            skipped_points.append((point, "Outside super-triangle (Numerical Error)"))
            continue

        spatial_index.remove(containing_entry)
        triangles.remove(containing_entry)
        a, b, c = containing_entry.vertices
        add_triangle(make_ccw(a, b, point))
        add_triangle(make_ccw(b, c, point))
        add_triangle(make_ccw(c, a, point))

        existing_points.add(point)

    return [entry.vertices for entry in triangles], skipped_points, super_triangle_vertices


class MeshTriangle:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = [v1, v2, v3] if cross_product(v1, v2, v3) >= 0 else [v1, v3, v2]
        self.neighbors = [None, None, None]

    def get_edge(self, index: int):
        v1 = self.vertices[(index + 1) % 3]
        v2 = self.vertices[(index + 2) % 3]
        return tuple(sorted((v1.id, v2.id)))

    def find_neighbor_index(self, other: "MeshTriangle") -> int:
        for index, neighbor in enumerate(self.neighbors):
            if neighbor == other:
                return index
        return -1


def build_topology(triangles):
    mesh = [MeshTriangle(*triangle) for triangle in triangles]
    edge_map = {}
    for triangle_index, triangle in enumerate(mesh):
        for edge_index in range(3):
            edge = triangle.get_edge(edge_index)
            if edge not in edge_map:
                edge_map[edge] = (triangle_index, edge_index)
                continue
            other_triangle_index, other_edge_index = edge_map[edge]
            triangle.neighbors[edge_index] = mesh[other_triangle_index]
            mesh[other_triangle_index].neighbors[other_edge_index] = triangle
    return mesh


def is_delaunay(mesh: list[MeshTriangle]) -> bool:
    """Checks if the mesh satisfies the Delaunay property."""
    for t1 in mesh:
        for i1, t2 in enumerate(t1.neighbors):
            if t2 is None:
                continue

            i2 = t2.find_neighbor_index(t1)
            a = t1.vertices[i1]
            b = t1.vertices[(i1 + 1) % 3]
            c = t1.vertices[(i1 + 2) % 3]
            d = t2.vertices[i2]

            if in_circle(a, b, c, d):
                return False
    return True


def get_nondelaunay_triangles(mesh: list[MeshTriangle]) -> set[MeshTriangle]:
    """Returns the set of triangles that violate the Delaunay property."""
    bad_triangles = set()
    for t1 in mesh:
        for i1, t2 in enumerate(t1.neighbors):
            if t2 is None:
                continue

            i2 = t2.find_neighbor_index(t1)
            a = t1.vertices[i1]
            b = t1.vertices[(i1 + 1) % 3]
            c = t1.vertices[(i1 + 2) % 3]
            d = t2.vertices[i2]

            if in_circle(a, b, c, d):
                bad_triangles.add(t1)
                bad_triangles.add(t2)
    return bad_triangles


class DTriangle:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.v = [v1, v2, v3] if cross_product(v1, v2, v3) >= 0 else [v1, v3, v2]
        self.n = [None, None, None]

    def set_neighbor(self, vertex_index: int, neighbor: "DTriangle | None"):
        self.n[vertex_index] = neighbor
        if neighbor is None:
            return
        for index in range(3):
            v1 = self.v[(vertex_index + 1) % 3]
            v2 = self.v[(vertex_index + 2) % 3]
            if neighbor.v[(index + 1) % 3] == v2 and neighbor.v[(index + 2) % 3] == v1:
                neighbor.n[index] = self
                break

    def has_vertex(self, point: Point) -> bool:
        return point in self.v

    def contains_point(self, point: Point) -> bool:
        return all(
            cross_product(self.v[index], self.v[(index + 1) % 3], point) >= -EPSILON
            for index in range(3)
        )


class DynamicDelaunay:
    def __init__(self, width=1000, height=1000):
        s1 = Point(width / 2, height * 10, id=-1)
        s2 = Point(-width * 10, -height * 10, id=-2)
        s3 = Point(width * 10, -height * 10, id=-3)
        self.super_vertices = [s1, s2, s3]
        self.triangles = {DTriangle(s1, s2, s3)}
        self.points = []

    def find_containing_triangle(self, point: Point):
        current = next(iter(self.triangles))
        visited = set()
        while current:
            visited.add(current)
            for index in range(3):
                if cross_product(current.v[(index + 1) % 3], current.v[(index + 2) % 3], point) > EPSILON:
                    if current.n[index] and current.n[index] not in visited:
                        current = current.n[index]
                        break
            else:
                return current
        return None

    def add_point(self, point: Point):
        triangle = self.find_containing_triangle(point)
        if triangle is None:
            return

        v0, v1, v2 = triangle.v
        n0, n1, n2 = triangle.n
        t0 = DTriangle(point, v1, v2)
        t1 = DTriangle(point, v2, v0)
        t2 = DTriangle(point, v0, v1)

        t0.n[0], t0.n[1], t0.n[2] = n0, t1, t2
        t1.n[0], t1.n[1], t1.n[2] = n1, t2, t0
        t2.n[0], t2.n[1], t2.n[2] = n2, t0, t1

        for index, old_neighbor in enumerate([n0, n1, n2]):
            if old_neighbor is None:
                continue
            for neighbor_index in range(3):
                if old_neighbor.n[neighbor_index] == triangle:
                    old_neighbor.n[neighbor_index] = [t1, t2, t0][index]
                    break

        self.triangles.remove(triangle)
        self.triangles.update([t0, t1, t2])
        self.points.append(point)
        self.legalize_edge(point, t0, 0)
        self.legalize_edge(point, t1, 0)
        self.legalize_edge(point, t2, 0)

    def legalize_edge(self, point: Point, triangle: DTriangle, index: int):
        neighbor = triangle.n[index]
        if neighbor is None:
            return

        neighbor_index = -1
        for probe in range(3):
            if neighbor.n[probe] == triangle:
                neighbor_index = probe
                break

        a, b, c = triangle.v[index], triangle.v[(index + 1) % 3], triangle.v[(index + 2) % 3]
        d = neighbor.v[neighbor_index]
        if not in_circle(a, b, c, d):
            return

        n_ab = triangle.n[(index + 2) % 3]
        n_ac = triangle.n[(index + 1) % 3]
        n_db = neighbor.n[(neighbor_index + 1) % 3]
        n_dc = neighbor.n[(neighbor_index + 2) % 3]

        triangle.v = [point, b, d]
        neighbor.v = [point, d, c]
        triangle.n = [n_db, neighbor, n_ab]
        neighbor.n = [n_dc, n_ac, triangle]

        if n_db:
            for probe in range(3):
                if n_db.v[(probe + 1) % 3] == d and n_db.v[(probe + 2) % 3] == b:
                    n_db.n[probe] = triangle
        if n_ac:
            for probe in range(3):
                if n_ac.v[(probe + 1) % 3] == a and n_ac.v[(probe + 2) % 3] == c:
                    n_ac.n[probe] = neighbor

        self.legalize_edge(point, triangle, 0)
        self.legalize_edge(point, neighbor, 0)

    def get_triangles(self):
        return [
            triangle.v
            for triangle in self.triangles
            if not any(vertex in self.super_vertices for vertex in triangle.v)
        ]

    def get_mesh(self) -> "TriangleMesh":
        """Returns the current triangulation as a TriangleMesh object."""
        return DelaunayMesher._to_triangle_mesh(self.get_triangles())


def _point_key(point: Point):
    return (round(point.x / EPSILON), round(point.y / EPSILON), point.id)


def _edge_key(a: Point, b: Point):
    return tuple(sorted((_point_key(a), _point_key(b))))


def _make_ccw_triangle(a: Point, b: Point, c: Point):
    return (a, b, c) if orientation_sign(a, b, c) >= 0 else (a, c, b)


def _build_edge_map(triangles):
    edge_map = {}
    for triangle_index, triangle in enumerate(triangles):
        for edge_index, edge in enumerate(((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0]))):
            edge_map.setdefault(_edge_key(*edge), []).append((triangle_index, edge_index, edge))
    return edge_map


def _quadrilateral_for_edge(first, second, shared_edge_key):
    shared_keys = set(shared_edge_key)
    first_opposite = next(vertex for vertex in first if _point_key(vertex) not in shared_keys)
    second_opposite = next(vertex for vertex in second if _point_key(vertex) not in shared_keys)
    shared_vertices = [vertex for vertex in first if _point_key(vertex) in shared_keys]
    a, b = shared_vertices
    return a, b, first_opposite, second_opposite


def _should_flip_constrained_edge(a: Point, b: Point, c: Point, d: Point) -> bool:
    if orientation_sign(c, a, d) == 0 or orientation_sign(c, d, b) == 0:
        return False
    if orientation_sign(c, a, b) == 0 or orientation_sign(d, a, b) == 0:
        return False
    if orientation_sign(c, a, d) < 0:
        a, d = d, a
    if orientation_sign(c, d, b) < 0:
        c, b = b, c
    if orientation_sign(c, d, a) == 0 or orientation_sign(c, d, b) == 0:
        return False
    return incircle_sign(c, a, d, b) > 0 or incircle_sign(c, d, b, a) > 0


def _point_on_boundary(point: Point, boundary: list[Point]) -> bool:
    return any(is_on_segment(point, boundary[index], boundary[(index + 1) % len(boundary)]) for index in range(len(boundary)))


def _proper_segment_intersection(a: Point, b: Point, c: Point, d: Point) -> bool:
    o1 = orientation_sign(a, b, c)
    o2 = orientation_sign(a, b, d)
    o3 = orientation_sign(c, d, a)
    o4 = orientation_sign(c, d, b)

    if o1 == 0 and is_on_segment(c, a, b):
        return False
    if o2 == 0 and is_on_segment(d, a, b):
        return False
    if o3 == 0 and is_on_segment(a, c, d):
        return False
    if o4 == 0 and is_on_segment(b, c, d):
        return False
    return o1 != o2 and o3 != o4


def _point_in_domain(point: Point, outer_boundary: list[Point], holes: list[list[Point]]) -> bool:
    from ..polygon.polygon import is_point_in_polygon
    if not is_point_in_polygon(point, outer_boundary):
        return False
    for hole in holes:
        if is_point_in_polygon(point, hole) and not _point_on_boundary(point, hole):
            return False
    return True


def _segment_valid_in_domain(
    start: Point,
    end: Point,
    outer_boundary: list[Point],
    holes: list[list[Point]],
    constrained_segments: set[tuple[tuple[int, int, int], tuple[int, int, int]]],
) -> bool:
    midpoint = Point((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not _point_in_domain(midpoint, outer_boundary, holes):
        return False

    for boundary in [outer_boundary, *holes]:
        for index, edge_start in enumerate(boundary):
            edge_end = boundary[(index + 1) % len(boundary)]
            if start == edge_start or start == edge_end or end == edge_start or end == edge_end:
                continue
            if _proper_segment_intersection(start, end, edge_start, edge_end):
                return False

    for edge in constrained_segments:
        if edge == _edge_key(start, end):
            continue
    return True


def constrained_delaunay_triangulation(outer_boundary: list[Point], holes: list[list[Point]] | None = None):
    from ..polygon.polygon import triangulate_polygon_with_holes
    holes = holes or []
    triangles, merged_polygon = triangulate_polygon_with_holes(outer_boundary, holes)
    constrained_edges = {
        _edge_key(merged_polygon[index], merged_polygon[(index + 1) % len(merged_polygon)])
        for index in range(len(merged_polygon))
    }

    changed = True
    while changed:
        changed = False
        edge_map = _build_edge_map(triangles)
        for edge_key, owners in edge_map.items():
            if edge_key in constrained_edges or len(owners) != 2:
                continue

            first_index, _, _ = owners[0]
            second_index, _, _ = owners[1]
            first = triangles[first_index]
            second = triangles[second_index]
            a, b, c, d = _quadrilateral_for_edge(first, second, edge_key)
            if orientation_sign(c, d, a) == 0 or orientation_sign(c, d, b) == 0:
                continue
            if not _segment_valid_in_domain(c, d, outer_boundary, holes, constrained_edges):
                continue
            if not _should_flip_constrained_edge(a, b, c, d):
                continue

            replacement_one = _make_ccw_triangle(c, d, a)
            replacement_two = _make_ccw_triangle(c, b, d)
            triangles[first_index] = replacement_one
            triangles[second_index] = replacement_two
            changed = True
            break

    return triangles, constrained_edges


__all__ = [
    "DTriangle",
    "DelaunayMesher",
    "DynamicDelaunay",
    "MeshTriangle",
    "Triangle",
    "build_topology",
    "constrained_delaunay_triangulation",
    "get_nondelaunay_triangles",
    "is_delaunay",
    "triangulate",
    "triangulate_divide_and_conquer",
]
