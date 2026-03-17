"""Topological queries for meshes."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .mesh_base import Mesh


class MeshTopology:
    """Provides topological queries for a mesh."""

    def __init__(self, mesh: Mesh):
        self._mesh = mesh
        self._v2v: Optional[Dict[int, Set[int]]] = None
        self._v2e: Optional[Dict[int, Set[int]]] = None
        self._e2e: Optional[Dict[int, Set[int]]] = None
        self._e2e_edge: Optional[Dict[int, Set[int]]] = None

    def vertex_neighbors(self, vertex_idx: int) -> Set[int]:
        """Returns the set of vertex indices adjacent to the given vertex."""
        if self._v2v is None:
            self._build_v2v()
        return self._v2v.get(vertex_idx, set())

    def vertex_elements(self, vertex_idx: int) -> Set[int]:
        """Returns the set of element indices (faces/cells) sharing the given vertex."""
        if self._v2e is None:
            self._build_v2e()
        return self._v2e.get(vertex_idx, set())

    def element_neighbors(self, element_idx: int) -> Set[int]:
        """Returns the set of element indices sharing at least one vertex."""
        if self._e2e is None:
            self._build_e2e()
        return self._e2e.get(element_idx, set())

    def shared_edge_neighbors(self, element_idx: int) -> Set[int]:
        """Returns the set of element indices sharing an edge (at least 2 vertices)."""
        if self._e2e_edge is None:
            self._build_e2e_edge()
        return self._e2e_edge.get(element_idx, set())

    def boundary_edges(self) -> List[Tuple[int, int]]:
        """Returns a list of edges (as vertex index pairs) that belong to only one element."""
        edge_count = defaultdict(int)
        
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for element in elements:
            for edge in self._get_element_edges(element):
                sorted_edge = tuple(sorted(edge))
                edge_count[sorted_edge] += 1
        
        return [edge for edge, count in edge_count.items() if count == 1]

    def _get_element_edges(self, v_indices: Tuple[int, ...]) -> List[Tuple[int, int]]:
        """Internal helper to decompose an element into its constituent edges."""
        n = len(v_indices)
        if self._mesh.cells and n == 4: # Tetrahedron: 6 edges
            v = v_indices
            return [
                (v[0], v[1]), (v[0], v[2]), (v[0], v[3]),
                (v[1], v[2]), (v[1], v[3]), (v[2], v[3])
            ]
        elif self._mesh.cells and n == 8: # Hexahedron: 12 edges
            v = v_indices
            return [
                (v[0], v[1]), (v[1], v[2]), (v[2], v[3]), (v[3], v[0]), # Bottom
                (v[4], v[5]), (v[5], v[6]), (v[6], v[7]), (v[7], v[4]), # Top
                (v[0], v[4]), (v[1], v[5]), (v[2], v[6]), (v[3], v[7])  # Verticals
            ]
        # Default for polygons
        return [(v_indices[i], v_indices[(i + 1) % n]) for i in range(n)]

    def boundary_faces(self) -> List[Tuple[int, ...]]:
        """Returns a list of faces (as vertex index tuples) that belong to only one cell."""
        if not self._mesh.cells:
            return []
            
        face_count = defaultdict(int)
        for cell in self._mesh.cells:
            for face in self._get_cell_faces(cell):
                canonical_face = tuple(sorted(face))
                face_count[canonical_face] += 1
                
        return [face for face, count in face_count.items() if count == 1]

    def _get_cell_faces(self, cell: Any) -> List[Tuple[int, ...]]:
        """Internal helper to decompose a cell into its constituent faces."""
        v = cell.v_indices
        n = len(v)
        if n == 4: # Tetrahedron
            return [
                (v[0], v[1], v[2]), (v[0], v[1], v[3]),
                (v[0], v[2], v[3]), (v[1], v[2], v[3])
            ]
        elif n == 8: # Hexahedron (standard VTK/finite element ordering)
            return [
                (v[0], v[3], v[2], v[1]), (v[4], v[5], v[6], v[7]), # Bottom, Top
                (v[0], v[1], v[5], v[4]), (v[1], v[2], v[6], v[5]), # Front, Right
                (v[2], v[3], v[7], v[6]), (v[3], v[0], v[4], v[7])  # Back, Left
            ]
        return [v] # Fallback for unknown or polygon-like cells

    def _build_v2v(self):
        self._v2v = defaultdict(set)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for element in elements:
            for u, v in self._get_element_edges(element):
                self._v2v[u].add(v)
                self._v2v[v].add(u)

    def _build_v2e(self):
        self._v2e = defaultdict(set)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for i, element in enumerate(elements):
            for v_idx in element:
                self._v2e[v_idx].add(i)

    def _build_e2e(self):
        """Builds adjacency based on shared vertices (at least one)."""
        if self._v2e is None:
            self._build_v2e()
        
        self._e2e = defaultdict(set)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for i, element in enumerate(elements):
            for v_idx in element:
                for neighbor_idx in self._v2e[v_idx]:
                    if neighbor_idx != i:
                        self._e2e[i].add(neighbor_idx)

    def _build_e2e_edge(self):
        """Builds adjacency based on shared edges (at least two vertices)."""
        self._e2e_edge = defaultdict(set)
        
        edge_map = defaultdict(list)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for i, element in enumerate(elements):
            for edge in self._get_element_edges(element):
                sorted_edge = tuple(sorted(edge))
                edge_map[sorted_edge].append(i)
        
        for sharing_elements in edge_map.values():
            if len(sharing_elements) > 1:
                for i in range(len(sharing_elements)):
                    for j in range(i + 1, len(sharing_elements)):
                        u, v = sharing_elements[i], sharing_elements[j]
                        self._e2e_edge[u].add(v)
                        self._e2e_edge[v].add(u)
