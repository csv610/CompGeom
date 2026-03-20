"""Discrete Morse Theory for triangle meshes."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict, Set, Optional, Any
from collections import deque

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh, Vertex, Face, HalfEdge

from compgeom.mesh.algorithms.dec import DEC

class DiscreteMorse:
    """
    Implements Discrete Morse Theory on a triangle mesh.
    Identifies critical points and builds a discrete gradient vector field.
    """
    def __init__(self, mesh: TriMesh, vertex_values: np.ndarray):
        self.mesh = mesh
        self.he_mesh = HalfEdgeMesh.from_triangle_mesh(mesh)
        self.dec = DEC(self.he_mesh)
        self.v_vals = vertex_values
        self.num_v = len(mesh.vertices)
        
        # Gradient Field: maps cell ID to its paired partner
        # We use a naming convention: 'v_idx', 'e_idx', 'f_idx'
        # To distinguish between dimensions, we use tuples: (dim, idx)
        self.gradient: Dict[Tuple[int, int], Tuple[int, int]] = {}
        self.critical_cells: Set[Tuple[int, int]] = set()
        
        self._compute_dgvf()

    def _compute_dgvf(self):
        """Constructs the Discrete Gradient Vector Field using Robins' Algorithm."""
        def vert_key(i):
            return (self.v_vals[i], i)
            
        sorted_v = sorted(range(self.num_v), key=vert_key)
        paired: Set[Tuple[int, int]] = set()
        
        for v_idx in sorted_v:
            v_key = vert_key(v_idx)
            
            # 1. Collect all cells in the Lower Star of v
            ls_edges = []
            neighbors = self.he_mesh.vertex_neighbors(v_idx)
            for nb in neighbors:
                if vert_key(nb) < v_key:
                    he = self.he_mesh.get_half_edge(v_idx, nb)
                    if he:
                        ls_edges.append(self.dec.edge_to_idx[he.idx])
            
            ls_faces = []
            for f_idx in self._get_incident_faces(v_idx):
                if max(vert_key(i) for i in self._get_face_vertex_indices(f_idx)) == v_key:
                    ls_faces.append(f_idx)

            # 2. Combinatorial Collapse of LS(v)
            # Cells in this star
            star_cells = { (0, v_idx) }
            for e in ls_edges: star_cells.add((1, e))
            for f in ls_faces: star_cells.add((2, f))
            
            def get_facets(dim, idx):
                if dim == 1:
                    he = self.he_mesh.edges[self.dec.primal_edges[idx].idx]
                    return [(0, he.vertex.idx), (0, he.next.vertex.idx)]
                if dim == 2:
                    return [(1, e) for e in self._get_face_edges(idx)]
                return []

            # Work on a local copy of cells in this star
            local_C = star_cells.copy()
            
            # Simple greedy collapse: 
            # Find a cell with exactly one facet in local_C
            while True:
                found = False
                # Try to pair (facet, cell)
                for cell in list(local_C):
                    if cell[0] == 0: continue # Vertices have no facets
                    
                    facets_in_star = [f for f in get_facets(cell[0], cell[1]) if f in local_C]
                    if len(facets_in_star) == 1:
                        facet = facets_in_star[0]
                        # Pair (facet, cell)
                        self.gradient[facet] = cell
                        self.gradient[cell] = facet
                        paired.add(facet)
                        paired.add(cell)
                        local_C.remove(facet)
                        local_C.remove(cell)
                        found = True
                        break
                if not found: break
                
            # Remaining cells in local_C are critical
            for cell in local_C:
                self.critical_cells.add(cell)

    def _get_face_he(self, f_idx: int) -> List[HalfEdge]:
        face = self.he_mesh.faces[f_idx]
        he = face.edge
        return [he, he.next, he.next.next]

    def _get_face_edges(self, f_idx: int) -> List[int]:
        return [self.dec.edge_to_idx[he.idx] for he in self._get_face_he(f_idx)]

    def get_critical_points(self) -> Dict[str, List[int]]:
        """Returns critical indices grouped by type."""
        res = {"minima": [], "saddles": [], "maxima": []}
        for dim, idx in self.critical_cells:
            if dim == 0: res["minima"].append(idx)
            elif dim == 1: res["saddles"].append(idx)
            elif dim == 2: res["maxima"].append(idx)
        return res

    def _get_incident_faces(self, v_idx: int) -> List[int]:
        """Returns the indices of faces incident to vertex v."""
        v = self.he_mesh.vertices[v_idx]
        faces = set()
        curr = v.edge
        if not curr: return []
        start = curr
        while True:
            if curr.face: faces.add(curr.face.idx)
            if not curr.twin: break
            curr = curr.twin.next
            if curr == start: break
        return list(faces)

    def _get_face_vertex_indices(self, f_idx: int) -> List[int]:
        """Returns the indices of the three vertices of a triangle face."""
        return [he.vertex.idx for he in self._get_face_he(f_idx)]

    def trace_ascending_path(self, saddle_edge_id: int) -> List[int]:
        """Traces a gradient path from a saddle upward to a maximum."""
        # TODO: Implement V-path tracing
        return []

    def get_euler_characteristic(self) -> int:
        """Computes the Euler characteristic from critical points."""
        crit = self.get_critical_points()
        return len(crit["minima"]) - len(crit["saddles"]) + len(crit["maxima"])
