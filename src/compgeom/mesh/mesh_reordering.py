"""Algorithms for mesh element and vertex reordering."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from .mesh import Mesh


class CuthillMcKee:
    """Provides implementations of the Cuthill-McKee reordering algorithm."""

    @staticmethod
    def reorder_elements(mesh: Mesh, reverse: bool = True) -> List[int]:
        """
        Computes a new ordering of mesh elements using the Cuthill-McKee algorithm.
        By default, it performs Reverse Cuthill-McKee (RCM).
        
        Returns:
            A list of original element indices in their new order.
        """
        n_elements = len(mesh.elements)
        if n_elements == 0:
            return []

        # Adjacency for elements (sharing an edge)
        adj = {i: mesh.topology.shared_edge_neighbors(i) for i in range(n_elements)}
        degrees = {i: len(adj[i]) for i in range(n_elements)}
        
        return CuthillMcKee._cuthill_mckee_core(n_elements, adj, degrees, reverse)

    @staticmethod
    def reorder_vertices(mesh: Mesh, reverse: bool = True) -> List[int]:
        """
        Computes a new ordering of mesh vertices using the Cuthill-McKee algorithm.
        
        Returns:
            A list of original vertex indices in their new order.
        """
        n_vertices = len(mesh.vertices)
        if n_vertices == 0:
            return []

        # Adjacency for vertices
        adj = {i: mesh.topology.vertex_neighbors(i) for i in range(n_vertices)}
        degrees = {i: len(adj[i]) for i in range(n_vertices)}
        
        return CuthillMcKee._cuthill_mckee_core(n_vertices, adj, degrees, reverse)

    @staticmethod
    def _cuthill_mckee_core(n: int, adj: Dict[int, Set[int]], degrees: Dict[int, int], reverse: bool) -> List[int]:
        permutation = []
        unvisited = set(range(n))
        
        while unvisited:
            # 1. Find starting node (min degree in component)
            start_node = min(unvisited, key=lambda i: degrees[i])
            
            # 2. BFS traversal
            queue = deque([start_node])
            unvisited.remove(start_node)
            
            while queue:
                u = queue.popleft()
                permutation.append(u)
                
                # Neighbors not yet visited, sorted by degree
                neighbors = sorted(
                    [v for v in adj[u] if v in unvisited],
                    key=lambda i: degrees[i]
                )
                
                for v in neighbors:
                    if v in unvisited:
                        unvisited.remove(v)
                        queue.append(v)
                        
        if reverse:
            return list(reversed(permutation))
        return permutation


__all__ = ["CuthillMcKee"]
