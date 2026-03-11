"""Unified interface for Delaunay triangulation algorithms."""

from __future__ import annotations
import math
from collections import deque
from typing import TYPE_CHECKING

from ...kernel import Point, in_circle, orientation_sign
from .delaunay_mesh_incremental import triangulate_incremental_fast
from .delaunay_dc import triangulate_divide_and_conquer
from .delaunay_naive import triangulate_naive, Triangle
from .delaunay_dynamic import DynamicDelaunay, DTriangle
from .delaunay_constrained import constrained_delaunay_triangulation
from .delaunay_mesh_edgeflip import triangulate_edgeflip
from .delaunay_topology import (
    MeshTriangle,
    build_topology,
    is_delaunay,
    get_nondelaunay_triangles,
)

if TYPE_CHECKING:
    from ..mesh import TriangleMesh


class DelaunayMesher:
    """
    A unified interface for Delaunay triangulation algorithms and utilities.
    
    Provides methods for incremental, divide and conquer, flip-based,
    dynamic, and constrained Delaunay triangulation.
    """

    @staticmethod
    def _to_triangle_mesh(triangles: list[tuple[Point, Point, Point]], skipped_points: list[tuple[Point, str]] | None = None) -> TriangleMesh:
        """Converts a list of Point triangles to a TriangleMesh object."""
        from ..mesh import TriangleMesh
        
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
    def triangulate(points: list[Point], algorithm: str = "incremental", spatial_sort: bool = True, jitter: bool = False, rejection_ratio: Optional[float] = None) -> TriangleMesh:
        """
        Performs Delaunay triangulation using the specified algorithm.
        
        Args:
            points: List of points to triangulate.
            algorithm: The algorithm to use ("incremental", "divide_and_conquer", "flip", or "edge_flip").
            spatial_sort: Whether to spatially sort points (improves incremental algorithms).
            jitter: Whether to add a tiny random jitter to points to prevent collinearity issues.
            rejection_ratio: If provided, filters out points that are closer than (rejection_ratio * bounding_box_scale).
            
        Returns:
            A TriangleMesh object.
        """
        if not points:
            return DelaunayMesher._to_triangle_mesh([])

        # Calculate bounding box for jitter and rejection scaling
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        scale = max(max_x - min_x, max_y - min_y, 1.0)

        skipped = []

        if rejection_ratio is not None:
            dist_threshold = scale * rejection_ratio
            filtered_points = []
            for p in points:
                too_close = False
                for existing in filtered_points:
                    if math.sqrt((p.x - existing.x)**2 + (p.y - existing.y)**2) < dist_threshold:
                        too_close = True
                        skipped.append((p, f"Point too close (threshold: {dist_threshold})"))
                        break
                if not too_close:
                    filtered_points.append(p)
            points = filtered_points

        if jitter:
            import random
            eps = scale * 1e-10
            jittered_points = []
            for p in points:
                pj = Point(
                    p.x + random.uniform(-eps, eps),
                    p.y + random.uniform(-eps, eps),
                    id=getattr(p, 'id', None)
                )
                jittered_points.append(pj)
            points = jittered_points

        if algorithm == "incremental":
            triangles, skipped = triangulate_incremental_fast(points, spatial_sort=spatial_sort)
        elif algorithm == "divide_and_conquer":
            triangles, skipped = triangulate_divide_and_conquer(points)
        elif algorithm == "edge_flip":
            triangles, skipped = triangulate_edgeflip(points, spatial_sort=spatial_sort)
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
    def merge(mesh1: TriangleMesh, mesh2: TriangleMesh, algorithm: str = "edge_flip") -> TriangleMesh:
        """
        Merges two Delaunay meshes into a single Delaunay mesh.
        
        Optimized Approach: Seeds the mesher with mesh1 and incrementally inserts 
        points from mesh2. This is significantly faster than starting from scratch
        if one mesh is large.
        """
        if algorithm != "edge_flip":
            # Fallback to from-scratch for other algorithms that don't support seeding yet
            all_points = list(set(mesh1.vertices) | set(mesh2.vertices))
            return DelaunayMesher.triangulate(all_points, algorithm=algorithm)
            
        from .delaunay_mesh_edgeflip import EdgeFlipDelaunayMesher
        mesher = EdgeFlipDelaunayMesher()
        
        # Triangulate points of mesh2 into the structure of mesh1
        triangles, skipped = mesher.triangulate(mesh2.vertices, existing_mesh=mesh1)
        
        return DelaunayMesher._to_triangle_mesh(triangles, skipped_points=skipped)

    @staticmethod
    def constrained_triangulate(outer_boundary: list[Point], holes: list[list[Point]] | None = None) -> TriangleMesh:
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

        def _make_ccw_triangle(a: Point, b: Point, c: Point):
            return (a, b, c) if orientation_sign(a, b, c) >= 0 else (a, c, b)

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

            if orientation_sign(a, d, b) * orientation_sign(a, d, c) >= 0 or \
               orientation_sign(b, c, a) * orientation_sign(b, c, d) >= 0:
                continue

            if not in_circle(a, b, c, d):
                continue

            flips_this_pass += 1
            
            n_ab = t1.neighbors[(i1 + 2) % 3]
            n_ca = t1.neighbors[(i1 + 1) % 3]
            n_bd = t2.neighbors[(i2 + 1) % 3]
            n_dc = t2.neighbors[(i2 + 2) % 3]

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

            if n_bd:
                idx = n_bd.find_neighbor_index(t2)
                if idx != -1: n_bd.neighbors[idx] = t1
            
            if n_ca:
                idx = n_ca.find_neighbor_index(t1)
                if idx != -1: n_ca.neighbors[idx] = t2
            
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


def triangulate(points: list[Point], algorithm: str = "incremental") -> TriangleMesh:
    """Standalone shortcut for DelaunayMesher.triangulate."""
    return DelaunayMesher.triangulate(points, algorithm)


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
    "triangulate_edgeflip",
]
