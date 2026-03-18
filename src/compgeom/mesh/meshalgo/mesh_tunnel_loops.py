"""
Identify tunnel loops in a mesh.
Tunnel loops are non-contractible cycles that go through the handles of a surface.
This implementation uses the tree-cotree decomposition to identify a homology basis,
consistent with the approach for finding significant loops on surfaces.
"""

from __future__ import annotations

import heapq
import math
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional

from compgeom.mesh import Mesh, MeshTopology


class MeshTunnelLoops:
    """
    Provides algorithms for identifying tunnel loops in a mesh.
    
    Uses a tree-cotree decomposition to find a basis for the first homology group 
    of the surface. This ensures that the identified loops are non-contractible
    and correspond to the topological "tunnels" of the mesh.
    """

    @staticmethod
    def _get_edges(mesh: Mesh) -> Set[Tuple[int, int]]:
        """Extracts unique sorted edges from the mesh topology."""
        edges = set()
        if hasattr(mesh, 'faces') and mesh.faces is not None and len(mesh.faces) > 0:
            for face in mesh.faces:
                v_indices = getattr(face, 'v_indices', face)
                for i in range(len(v_indices)):
                    u, v = v_indices[i], v_indices[(i + 1) % len(v_indices)]
                    edges.add(tuple(sorted((u, v))))
        else:
            topo = MeshTopology(mesh)
            n_vertices = len(mesh.vertices)
            for i in range(n_vertices):
                for neighbor in topo.vertex_neighbors(i):
                    edges.add(tuple(sorted((i, neighbor))))
        return edges

    @staticmethod
    def _get_adjacency(mesh: Mesh) -> Dict[int, List[int]]:
        """Builds an adjacency list for the mesh vertices."""
        adj = defaultdict(list)
        if hasattr(mesh, 'faces') and mesh.faces is not None and len(mesh.faces) > 0:
            for face in mesh.faces:
                v_indices = getattr(face, 'v_indices', face)
                for i in range(len(v_indices)):
                    u, v = v_indices[i], v_indices[(i + 1) % len(v_indices)]
                    adj[u].append(v)
                    adj[v].append(u)
        else:
            topo = MeshTopology(mesh)
            n_vertices = len(mesh.vertices)
            for i in range(n_vertices):
                for neighbor in topo.vertex_neighbors(i):
                    adj[i].append(neighbor)
                    adj[neighbor].append(i)
        
        for u in adj:
            adj[u] = list(set(adj[u]))
        return adj

    @staticmethod
    def _get_edge_faces(mesh: Mesh) -> Dict[Tuple[int, int], List[int]]:
        """Maps each edge to the indices of faces it bounds."""
        edge_faces = defaultdict(list)
        if hasattr(mesh, 'faces') and mesh.faces is not None:
            for i, face in enumerate(mesh.faces):
                v_indices = getattr(face, 'v_indices', face)
                for j in range(len(v_indices)):
                    u, v = v_indices[j], v_indices[(j + 1) % len(v_indices)]
                    edge_faces[tuple(sorted((u, v)))].append(i)
        return edge_faces

    @staticmethod
    def _calculate_topology(mesh: Mesh) -> Tuple[int, int]:
        """Calculates Euler characteristic and genus of the mesh."""
        V = len(mesh.vertices)
        edges = MeshTunnelLoops._get_edges(mesh)
        E = len(edges)
        
        F = 0
        if hasattr(mesh, 'faces') and mesh.faces is not None:
            F = len(mesh.faces)
        elif hasattr(mesh, 'cells') and mesh.cells is not None:
            F = len(mesh.cells)
        
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
        start_node = next(iter(adj)) if adj else 0
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
    def _dual_spanning_tree(mesh: Mesh, edge_faces: Dict[Tuple[int, int], List[int]]) -> Set[Tuple[int, int]]:
        """Computes a spanning tree of the dual graph (cotree)."""
        num_faces = len(mesh.faces) if hasattr(mesh, 'faces') and mesh.faces else 0
        if num_faces == 0:
            return set()
            
        dual_adj = defaultdict(list)
        for flist in edge_faces.values():
            if len(flist) == 2:
                f1, f2 = flist
                dual_adj[f1].append(f2)
                dual_adj[f2].append(f1)
                
        visited = set()
        start_face = 0
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
    def _edge_length(u: int, v: int, vertices) -> float:
        """Calculates Euclidean distance between two vertices."""
        p1 = vertices[u]
        p2 = vertices[v]
        if hasattr(p1, 'x') and hasattr(p1, 'y'):
            z1 = getattr(p1, 'z', 0.0)
            z2 = getattr(p2, 'z', 0.0)
            return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (z1 - z2)**2)
        else:
            return math.sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))

    @staticmethod
    def _dijkstra(u: int, vertices, adj: Dict[int, List[int]]) -> Dict[int, Optional[int]]:
        """Runs Dijkstra's algorithm to find shortest paths from start vertex u."""
        dist = {u: 0.0}
        parent = {u: None}
        pq = [(0.0, u)]
        while pq:
            d, curr = heapq.heappop(pq)
            if d > dist.get(curr, float('inf')):
                continue
            for v in adj[curr]:
                weight = MeshTunnelLoops._edge_length(curr, v, vertices)
                new_dist = d + weight
                if new_dist < dist.get(v, float('inf')):
                    dist[v] = new_dist
                    parent[v] = curr
                    heapq.heappush(pq, (new_dist, v))
        return parent

    @staticmethod
    def identify_tunnels(mesh: Mesh) -> List[List[int]]:
        """
        Identifies tunnel loops in the input mesh.
        
        Args:
            mesh: The Mesh object.
            
        Returns:
            A list of loops, where each loop is a list of vertex indices.
        """
        if not mesh.vertices or not mesh.faces:
            return []
            
        adj = MeshTunnelLoops._get_adjacency(mesh)
        edges = MeshTunnelLoops._get_edges(mesh)
        edge_faces = MeshTunnelLoops._get_edge_faces(mesh)
        
        primal_tree = MeshTunnelLoops._primal_spanning_tree(mesh, adj)
        dual_tree = MeshTunnelLoops._dual_spanning_tree(mesh, edge_faces)
        
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
                # Boundary edges are generally not part of tunnel loops for closed surfaces
                pass

        loops_with_len = []
        for u, v in generators:
            # Find the shortest path between endpoints of the generator edge
            # without using the generator edge itself. This ensures we find a
            # proper cycle instead of just the edge.
            
            # Temporarily remove the edge from the adjacency
            adj[u].remove(v)
            adj[v].remove(u)
            
            parent_map = MeshTunnelLoops._dijkstra(u, mesh.vertices, adj)
            
            # Restore the edge
            adj[u].append(v)
            adj[v].append(u)
            
            if v in parent_map:
                path = []
                curr = v
                while curr is not None:
                    path.append(curr)
                    curr = parent_map[curr]
                
                L = 0.0
                for i in range(len(path) - 1):
                    L += MeshTunnelLoops._edge_length(path[i], path[i+1], mesh.vertices)
                L += MeshTunnelLoops._edge_length(path[-1], path[0], mesh.vertices)
                
                loops_with_len.append((L, path))
                
        loops_with_len.sort(key=lambda x: x[0])
        
        _, genus = MeshTunnelLoops._calculate_topology(mesh)
        needed = max(1, 2 * genus)
        
        return [loop for _, loop in loops_with_len[:needed]]


__all__ = ["MeshTunnelLoops"]
