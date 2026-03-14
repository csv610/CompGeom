"""Mesh element and vertex coloring algorithms."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from ..mesh import Mesh


class MeshColoring:
    """Provides algorithms for mesh element and vertex coloring."""

    @staticmethod
    def color_elements(mesh: Mesh) -> Dict[int, int]:
        """
        Colors the elements (faces/cells) of a mesh using a greedy algorithm.
        Ensures that elements sharing an edge (at least 2 vertices) have different colors.
        
        Returns:
            A dictionary mapping element index to a color ID (integer).
        """
        n_elements = len(mesh.elements)
        coloring: Dict[int, int] = {}
        
        # Greedy coloring
        for i in range(n_elements):
            # Find colors used by neighbors (sharing an edge)
            neighbor_indices = mesh.topology.shared_edge_neighbors(i)
            neighbor_colors = {coloring[n] for n in neighbor_indices if n in coloring}
            
            # Assign the smallest available color
            color = 0
            while color in neighbor_colors:
                color += 1
            coloring[i] = color
            
        return coloring

    @staticmethod
    def color_vertices(mesh: Mesh) -> Dict[int, int]:
        """
        Colors the vertices of a mesh using a greedy algorithm.
        Ensures that adjacent vertices (sharing an edge) have different colors.
        
        Returns:
            A dictionary mapping vertex index to a color ID (integer).
        """
        n_vertices = len(mesh.vertices)
        coloring: Dict[int, int] = {}
        
        # Greedy coloring
        for i in range(n_vertices):
            # Find colors used by neighbor vertices
            neighbor_indices = mesh.topology.vertex_neighbors(i)
            neighbor_colors = {coloring[n] for n in neighbor_indices if n in coloring}
            
            # Assign the smallest available color
            color = 0
            while color in neighbor_colors:
                color += 1
            coloring[i] = color
            
        return coloring


__all__ = ["MeshColoring"]
