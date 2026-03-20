"""
Identify cut loops in a mesh.
Cut loops are non-contractible cycles that, when cut along, 
help in reducing the genus of the surface.
This implementation uses the tree-cotree decomposition to identify 
a basis for the first homology group of the surface.
"""

from __future__ import annotations

import heapq
import math
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional, Any

from compgeom.mesh import Mesh, MeshTopology


class MeshCutLoop:
    """
    Provides algorithms for identifying cut loops in a mesh.
    
    Uses a tree-cotree decomposition to find a basis for the first homology group 
    of the surface. This ensures that the identified loops are non-contractible.
    """

    @staticmethod
    def _get_edges(mesh: Mesh) -> Set[Tuple[int, int]]:
        """Extracts unique sorted edges from the mesh topology."""
        return MeshTopology(mesh).get_edges()

    @staticmethod
    def _get_adjacency(mesh: Mesh) -> Dict[int, List[int]]:
        """Builds an adjacency list for the mesh vertices."""
        n_vertices = len(mesh.vertices)
        topo = MeshTopology(mesh)
        return {i: list(topo.vertex_neighbors(i)) for i in range(n_vertices)}

    @staticmethod
    def _get_edge_faces(mesh: Mesh) -> Dict[Tuple[int, int], List[int]]:
        """Maps each edge to the indices of faces (or cells) it bounds."""
        edge_faces = {}
        n_vertices = len(mesh.vertices)
        topo = MeshTopology(mesh)
        for i in range(n_vertices):
            for neighbor in topo.vertex_neighbors(i):
                if i < neighbor:
                    edge = (i, neighbor)
                    # MeshTopology.vertex_elements returns a Set[int] of faces/cells
                    # sharing the vertex. The intersection gives those sharing the edge.
                    faces = topo.vertex_elements(i) & topo.vertex_elements(neighbor)
                    edge_faces[edge] = list(faces)
        return edge_faces

    @staticmethod
    def _calculate_topology(mesh: Mesh) -> Tuple[int, int]:
        """Calculates Euler characteristic and genus of the mesh."""
        V = len(mesh.vertices)
        edges = MeshCutLoop._get_edges(mesh)
        E = len(edges)
        
        # F is the number of faces (for surface meshes) or cells (for volume meshes)
        F = len(mesh.cells) if mesh.cells else len(mesh.faces)
        
        chi = V - E + F
        genus = max(0, (2 - chi) // 2)
        return chi, genus

    @staticmethod
    def _primal_spanning_tree(mesh: Mesh, adj: Dict[int, List[int]]) -> Set[Tuple[int, int]]:
        """Computes a spanning tree of the primal graph."""
        if not mesh.vertices:
            return set()
        parent = {}
        visited = set()
        # Find any node that has neighbors
        start_node = next((node for node, neighbors in adj.items() if neighbors), 0)
        stack = [start_node]
        parent[start_node] = None
        visited.add(start_node)
        
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    parent[v] = u
                    stack.append(v)
        
        tree_edges = set()
        for v, p in parent.items():
            if p is not None:
                tree_edges.add(tuple(sorted((v, p))))
        return tree_edges

    @staticmethod
    def _dual_spanning_tree(mesh: Mesh, edge_faces: Dict[Tuple[int, int], List[int]], primal_tree: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Computes a spanning tree of the dual graph (cotree) using only edges not in the primal tree."""
        num_faces = len(mesh.cells) if mesh.cells else (len(mesh.faces) if mesh.faces else 0)
        if num_faces == 0:
            return set()
            
        dual_adj = defaultdict(list)
        for e, flist in edge_faces.items():
            # Only consider edges shared by exactly two faces/cells that are NOT in the primal tree
            if len(flist) == 2 and e not in primal_tree:
                f1, f2 = flist
                dual_adj[f1].append(f2)
                dual_adj[f2].append(f1)
                
        visited = set()
        # Find a starting face that is in the dual adjacency
        start_face = next(iter(dual_adj)) if dual_adj else None
        
        if start_face is None:
            return set()
                    
        stack = [start_face]
        visited.add(start_face)
        
        tree_faces = set()
        while stack:
            u = stack.pop()
            for v in dual_adj[u]:
                if v not in visited:
                    visited.add(v)
                    tree_faces.add(tuple(sorted((u, v))))
                    stack.append(v)
        return tree_faces

    @staticmethod
    def _edge_length(u: int, v: int, vertices: List[Any]) -> float:
        """Calculates Euclidean distance between two vertices."""
        p1, p2 = vertices[u], vertices[v]
        def get_coords(p):
            if hasattr(p, 'x') and hasattr(p, 'y'):
                return (p.x, p.y, getattr(p, 'z', 0.0))
            return p
        c1, c2 = get_coords(p1), get_coords(p2)
        return math.sqrt(sum((a - b)**2 for a, b in zip(c1, c2)))

    @staticmethod
    def _dijkstra(u: int, vertices: List[Any], adj: Dict[int, List[int]]) -> Dict[int, Optional[int]]:
        """Runs Dijkstra's algorithm to find shortest paths from start vertex u."""
        dist = {u: 0.0}
        parent = {u: None}
        pq = [(0.0, u)]
        while pq:
            d, curr = heapq.heappop(pq)
            if d > dist.get(curr, float('inf')):
                continue
            for v in adj[curr]:
                weight = MeshCutLoop._edge_length(curr, v, vertices)
                new_dist = d + weight
                if new_dist < dist.get(v, float('inf')):
                    dist[v] = new_dist
                    parent[v] = curr
                    heapq.heappush(pq, (new_dist, v))
        return parent

    @classmethod
    def identify_cut_loops(cls, mesh: Mesh) -> List[List[int]]:
        """
        Identifies cut loops in the input mesh.
        
        Args:
            mesh: The Mesh object.
            
        Returns:
            A list of loops, where each loop is a list of vertex indices.
        """
        if not mesh.vertices or (not mesh.faces and not mesh.cells):
            return []
            
        adj = cls._get_adjacency(mesh)
        edges = cls._get_edges(mesh)
        edge_faces = cls._get_edge_faces(mesh)
        
        primal_tree = cls._primal_spanning_tree(mesh, adj)
        dual_tree = cls._dual_spanning_tree(mesh, edge_faces, primal_tree)
        
        # Generator edges are those neither in the primal tree nor in the dual tree.
        generators = []
        for e in edges:
            if e in primal_tree:
                continue
            
            flist = edge_faces[e]
            if len(flist) == 2:
                f1, f2 = flist
                if tuple(sorted((f1, f2))) in dual_tree:
                    continue
                generators.append(e)
            elif len(flist) == 1:
                # Boundary edges are not in primal tree but have no dual edge.
                # In a tree-cotree decomposition of a surface with boundary,
                # these can also be generators.
                generators.append(e)
        
        # Build adjacency for the primal tree only
        tree_adj = defaultdict(list)
        for u_e, v_e in primal_tree:
            tree_adj[u_e].append(v_e)
            tree_adj[v_e].append(u_e)

        loops_with_len = []
        for u, v in generators:
            # Find the path between endpoints using ONLY the primal tree.
            # Since it's a tree, there's a unique path.
            parent_map = cls._dijkstra(u, mesh.vertices, tree_adj)
            
            if v in parent_map:
                path = []
                curr = v
                while curr is not None:
                    path.append(curr)
                    curr = parent_map[curr]
                
                L = 0.0
                for i in range(len(path) - 1):
                    L += cls._edge_length(path[i], path[i+1], mesh.vertices)
                # Closing generator edge
                L += cls._edge_length(path[-1], path[0], mesh.vertices)
                
                loops_with_len.append((L, path))
                
        loops_with_len.sort(key=lambda x: x[0])
        
        _, genus = cls._calculate_topology(mesh)
        needed = max(1, 2 * genus)
        
        return [loop for _, loop in loops_with_len[:needed]]


__all__ = ["MeshCutLoop"]
