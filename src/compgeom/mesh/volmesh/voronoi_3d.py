from __future__ import annotations
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict
import math

from ...kernel import Point3D
from .tetmesh.delaunay_tetmesh import DelaunayTetMesher
from .tetmesh.utils import get_tet_circumcenter
from .polyhedral_mesh import PolyhedralMesh

class VoronoiDiagram3D:
    """
    Computes and stores a Voronoi Diagram for a set of points in 3D space.
    The Voronoi cells are convex polyhedra.
    Infinite cells are not handled explicitly (they would correspond to points on the boundary of the Delaunay triangulation).
    """

    def __init__(self):
        self.points: List[Point3D] = []
        self.vertices: List[Point3D] = []  # Voronoi vertices (Delaunay circumcenters)
        self.cells: List[List[List[int]]] = []  # Each cell is a list of faces. Each face is a list of vertex indices.

    def compute(self, points: List[Point3D]) -> PolyhedralMesh:
        """
        Computes the Voronoi diagram using the Delaunay Dual property.
        """
        if not points:
            return PolyhedralMesh([], [])

        self.points = points
        
        # 1. Compute Delaunay Tetrahedralization (keeping super-tetrahedron tets for infinite cells)
        from .tetmesh.delaunay_mesh_incremental import IncrementalDelaunayMesher3D
        mesher = IncrementalDelaunayMesher3D()
        mesher.triangulate(points)
        
        # Get ALL tets (including those connected to super-vertices)
        all_tets = [tuple(t.vertices) for t in mesher.active_tets]
        
        # 2. Compute circumcenters for all tetrahedra
        self.vertices = []
        tet_circumcenters = []
        for tet in all_tets:
            center, radius = get_tet_circumcenter(tet[0], tet[1], tet[2], tet[3])
            tet_circumcenters.append(center)
        
        self.vertices = tet_circumcenters
        
        # 3. Build unique point list and map points to their indices
        unique_points = []
        point_to_idx = {}
        # Include original points and super-vertices
        all_input_points = list(points) + list(mesher.super_vertices)
        for p in all_input_points:
            if p not in point_to_idx:
                point_to_idx[p] = len(unique_points)
                unique_points.append(p)
        
        # Map tets to vertex indices
        tet_indices_list = []
        for tet in all_tets:
            tet_indices_list.append(tuple(point_to_idx[v] for v in tet))

        # Map Delaunay edges to the tetrahedra that share them
        edge_to_tets = defaultdict(list)
        for tet_idx, indices in enumerate(tet_indices_list):
            # There are 6 edges in a tetrahedron
            edges = [
                tuple(sorted((indices[0], indices[1]))),
                tuple(sorted((indices[0], indices[2]))),
                tuple(sorted((indices[0], indices[3]))),
                tuple(sorted((indices[1], indices[2]))),
                tuple(sorted((indices[1], indices[3]))),
                tuple(sorted((indices[2], indices[3])))
            ]
            for edge in edges:
                edge_to_tets[edge].append(tet_idx)

        # Map each vertex to its neighbors in Delaunay
        vertex_neighbors = defaultdict(set)
        for v1, v2 in edge_to_tets.keys():
            vertex_neighbors[v1].add(v2)
            vertex_neighbors[v2].add(v1)

        voronoi_cells = []
        
        # Only build cells for the original input points
        for i in range(len(points)):
            p_idx = point_to_idx[points[i]]
            cell_faces = []
            neighbors = vertex_neighbors[p_idx]
            
            for j_idx in neighbors:
                edge = tuple(sorted((p_idx, j_idx)))
                sharing_tets = edge_to_tets[edge]
                
                if len(sharing_tets) < 3:
                    continue
                
                ordered_face_v_indices = self._order_face_vertices_by_connectivity(sharing_tets, tet_indices_list, edge)
                if ordered_face_v_indices:
                    cell_faces.append(ordered_face_v_indices)
            
            voronoi_cells.append(cell_faces)

        return PolyhedralMesh(self.vertices, voronoi_cells, seeds=self.points)

    def _order_face_vertices_by_connectivity(self, tet_indices: List[int], all_tet_indices: List[Tuple[int, ...]], edge: Tuple[int, int]) -> List[int]:
        """Orders the circumcenters of the tetrahedra sharing an edge."""
        tet_adj = defaultdict(list)
        for i in range(len(tet_indices)):
            for j in range(i + 1, len(tet_indices)):
                idx_i = tet_indices[i]
                idx_j = tet_indices[j]
                tet_i = set(all_tet_indices[idx_i])
                tet_j = set(all_tet_indices[idx_j])
                shared = tet_i.intersection(tet_j)
                if len(shared) == 3:
                    tet_adj[idx_i].append(idx_j)
                    tet_adj[idx_j].append(idx_i)
        
        if not tet_adj:
            return []

        start_node = tet_indices[0]
        ordered = []
        curr = start_node
        visited = {curr}
        ordered.append(curr)
        
        while True:
            next_node = None
            for neighbor in tet_adj[curr]:
                if neighbor not in visited:
                    next_node = neighbor
                    break
            if next_node is None:
                break
            visited.add(next_node)
            ordered.append(next_node)
            curr = next_node
            
        return ordered
