"""Algorithms for mesh element and vertex reordering."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from compgeom.mesh.mesh_base import Mesh
from compgeom.mesh.mesh_topology import MeshTopology


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
        n_elements = len(mesh.cells) if mesh.cells else len(mesh.faces)
        if n_elements == 0:
            return []

        # Adjacency for elements (sharing an edge)
        topo = MeshTopology(mesh)
        adj = {i: topo.shared_edge_neighbors(i) for i in range(n_elements)}
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
        topo = MeshTopology(mesh)
        adj = {i: topo.vertex_neighbors(i) for i in range(n_vertices)}
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


class MeshReorderer:
    """Provides methods for applying reorderings to a mesh."""

    @staticmethod
    def reorder_nodes(mesh: Mesh, new_node_indices: List[int]):
        """
        Renumbers the nodes and updates element connectivity.
        """
        from dataclasses import replace
        from compgeom.mesh.mesh_topology import MeshTopology

        if len(new_node_indices) != len(mesh.nodes):
            raise ValueError("new_node_indices must have the same length as nodes.")

        old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(new_node_indices)}
        
        # New nodes with updated IDs
        new_nodes = []
        for new_idx, old_idx in enumerate(new_node_indices):
            node = mesh.nodes[old_idx]
            new_nodes.append(replace(node, id=new_idx))
        
        # Access protected members to update mesh state
        mesh._nodes = new_nodes

        # Update edges
        new_edges = []
        for edge in mesh.edges:
            new_v = tuple(old_to_new[v_idx] for v_idx in edge.v_indices)
            new_edges.append(replace(edge, v_indices=new_v))
        mesh._edges = new_edges

        # Update faces
        new_faces = []
        for face in mesh.faces:
            new_v = tuple(old_to_new[v_idx] for v_idx in face.v_indices)
            new_faces.append(replace(face, v_indices=new_v))
        mesh._faces = new_faces

        # Update cells
        new_cells = []
        for cell in mesh.cells:
            new_v = tuple(old_to_new[v_idx] for v_idx in cell.v_indices)
            new_cells.append(replace(cell, v_indices=new_v))
        mesh._cells = new_cells

        mesh._topology = MeshTopology(mesh)


__all__ = ["CuthillMcKee", "MeshReorderer"]
