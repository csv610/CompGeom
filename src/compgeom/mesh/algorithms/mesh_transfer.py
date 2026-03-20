"""Algorithms for transferring mesh topology between geometric domains."""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple, Union

from compgeom.kernel import Point2D, Point3D
from compgeom.kernel import distance
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.mesh_topology import MeshTopology


class MeshTransfer:
    """Transfers triangulation from one polygonal domain to another with minimum distortion."""

    @staticmethod
    def transfer(source_mesh: TriMesh, target_polygon: List[Point2D]) -> TriMesh:
        """
        Transfers the topology of source_mesh to the domain defined by target_polygon.
        Uses Harmonic Mapping (Barycentric Mapping) to minimize distortion.
        
        Args:
            source_mesh: The original mesh providing the topology.
            target_polygon: List of Points defining the new boundary.
            
        Returns:
            A new TriMesh with source topology and target geometry.
        """
        # 1. Extract boundary of the source mesh
        topo = MeshTopology(source_mesh)
        boundary_edges = topo.boundary_edges()
        if not boundary_edges:
            raise ValueError("Source mesh has no boundary.")

        # Build boundary cycle
        adj = defaultdict(list)
        for u, v in boundary_edges:
            adj[u].append(v)
            adj[v].append(u)

        # Start from an arbitrary boundary vertex
        start_node = boundary_edges[0][0]
        cycle = [start_node]
        curr = adj[start_node][0]
        prev = start_node
        while curr != start_node:
            cycle.append(curr)
            # Find next
            next_node = adj[curr][0] if adj[curr][0] != prev else adj[curr][1]
            prev, curr = curr, next_node

        # 2. Parameterize source boundary (normalized arc-length)
        source_arc_lengths = [0.0]
        total_p = 0.0
        for i in range(len(cycle)):
            p1 = source_mesh.vertices[cycle[i]]
            p2 = source_mesh.vertices[cycle[(i + 1) % len(cycle)]]
            d = distance(p1, p2)
            total_p += d
            source_arc_lengths.append(total_p)
        
        normalized_source = [s / total_p for s in source_arc_lengths]

        # 3. Parameterize target boundary
        target_arc_lengths = [0.0]
        total_target_p = 0.0
        for i in range(len(target_polygon)):
            p1 = target_polygon[i]
            p2 = target_polygon[(i + 1) % len(target_polygon)]
            d = distance(p1, p2)
            total_target_p += d
            target_arc_lengths.append(total_target_p)
        
        normalized_target = [s / total_target_p for s in target_arc_lengths]

        # 4. Map source boundary vertices to target boundary positions
        new_vertices_coords = [None] * len(source_mesh.vertices)
        
        def interpolate_target(t: float) -> Point2D:
            # t is normalized distance [0, 1]
            # Find which segment of target_polygon it falls into
            for i in range(len(normalized_target) - 1):
                if normalized_target[i] <= t <= normalized_target[i+1]:
                    segment_t = (t - normalized_target[i]) / (normalized_target[i+1] - normalized_target[i])
                    p1 = target_polygon[i]
                    p2 = target_polygon[(i+1) % len(target_polygon)]
                    return Point2D(
                        p1.x + segment_t * (p2.x - p1.x),
                        p1.y + segment_t * (p2.y - p1.y)
                    )
            return target_polygon[0]

        for i, v_idx in enumerate(cycle):
            new_vertices_coords[v_idx] = interpolate_target(normalized_source[i])

        # 5. Initialize interior vertices (mean of target boundary or simple centroid)
        target_centroid_x = sum(p.x for p in target_polygon) / len(target_polygon)
        target_centroid_y = sum(p.y for p in target_polygon) / len(target_polygon)
        
        boundary_indices = set(cycle)
        for i in range(len(source_mesh.vertices)):
            if i not in boundary_indices:
                new_vertices_coords[i] = Point2D(target_centroid_x, target_centroid_y)

        # 6. Iterative Harmonic Solver (Gauss-Seidel)
        # Solve Laplace equation: L V = 0 where L is Laplacian operator
        # Vi = average of its neighbors
        for _ in range(200): # Convergence iterations
            max_diff = 0.0
            for i in range(len(source_mesh.vertices)):
                if i in boundary_indices:
                    continue
                
                neighbors = topo.vertex_neighbors(i)
                if not neighbors:
                    continue
                
                sum_x = sum(new_vertices_coords[nb].x for nb in neighbors)
                sum_y = sum(new_vertices_coords[nb].y for nb in neighbors)
                
                new_x = sum_x / len(neighbors)
                new_y = sum_y / len(neighbors)
                
                diff = abs(new_vertices_coords[i].x - new_x) + abs(new_vertices_coords[i].y - new_y)
                max_diff = max(max_diff, diff)
                
                new_vertices_coords[i] = Point2D(new_x, new_y, i)
            
            if max_diff < 1e-6:
                break

        return TriMesh(new_vertices_coords, source_mesh.faces)


from collections import defaultdict
__all__ = ["MeshTransfer"]
