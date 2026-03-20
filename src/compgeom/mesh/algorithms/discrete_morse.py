"""Discrete Morse Theory for triangle meshes."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict, Set, Optional, Any
from collections import deque

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh, Vertex, Face, HalfEdge

class DiscreteMorse:
    """
    Implements Discrete Morse Theory on a triangle mesh.
    Identifies critical points and builds a discrete gradient vector field.
    """
    def __init__(self, mesh: TriMesh, vertex_values: np.ndarray):
        self.mesh = mesh
        self.he_mesh = HalfEdgeMesh.from_triangle_mesh(mesh)
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
                        edge_id = min(he.idx, he.twin.idx) if he.twin else he.idx
                        ls_edges.append(edge_id)
            
            ls_faces = []
            incident_faces = self._get_incident_faces(v_idx)
            for f_idx in incident_faces:
                v_indices = self._get_face_vertex_indices(f_idx)
                if max(vert_key(i) for i in v_indices) == v_key:
                    ls_faces.append(f_idx)

            # 2. Process the Lower Star (Robins' pairing)
            E = set(ls_edges)
            F = set(ls_faces)
            
            queue = deque()
            
            if not E:
                self.critical_cells.add((0, v_idx))
            else:
                # Pair v with the first edge
                e_pair = sorted(list(E))[0]
                self.gradient[(0, v_idx)] = (1, e_pair)
                self.gradient[(1, e_pair)] = (0, v_idx)
                paired.add((0, v_idx))
                paired.add((1, e_pair))
                E.remove(e_pair)
                
                # Maintain a queue of faces that have exactly one unpaired edge in E
                def update_queue():
                    for f in list(F):
                        if (2, f) in paired: continue
                        unpaired_edges = [e for e in self._get_face_edges(f) if e in E]
                        if len(unpaired_edges) == 1:
                            queue.append((f, unpaired_edges[0]))

                update_queue()
                while queue:
                    f, e = queue.popleft()
                    if (2, f) in paired or (1, e) not in E: continue
                    
                    self.gradient[(2, f)] = (1, e)
                    self.gradient[(1, e)] = (2, f)
                    paired.add((2, f))
                    paired.add((1, e))
                    E.remove(e)
                    update_queue()
                
                # Remaining are critical
                for e in E:
                    if (1, e) not in paired: self.critical_cells.add((1, e))
                for f in F:
                    if (2, f) not in paired: self.critical_cells.add((2, f))

    def get_critical_points(self) -> Dict[str, List[int]]:
        """Returns critical indices grouped by type."""
        res = {"minima": [], "saddles": [], "maxima": []}
        for dim, idx in self.critical_cells:
            if dim == 0: res["minima"].append(idx)
            elif dim == 1: res["saddles"].append(idx)
            elif dim == 2: res["maxima"].append(idx)
        return res

    def _get_incident_faces(self, v_idx: int) -> List[int]:
        v = self.he_mesh.vertices[v_idx]
        faces = set()
        curr = v.edge
        if not curr: return []
        while True:
            if curr.face: faces.add(curr.face.idx)
            if not curr.twin: break
            curr = curr.twin.next
            if curr == v.edge: break
        return list(faces)

    def _get_other_vert(self, edge_id: int, v_idx: int) -> int:
        he = self.he_mesh.edges[edge_id]
        return he.next.vertex.idx if he.vertex.idx == v_idx else he.vertex.idx

    def _get_face_edges(self, f_idx: int) -> List[int]:
        face = self.he_mesh.faces[f_idx]
        he = face.edge
        edges = []
        for _ in range(3):
            edge_id = min(he.idx, he.twin.idx) if he.twin else he.idx
            edges.append(edge_id)
            he = he.next
        return edges

    def _get_face_vertex_indices(self, f_idx: int) -> List[int]:
        """Returns the indices of the three vertices of a triangle face."""
        face = self.he_mesh.faces[f_idx]
        he = face.edge
        v_indices = []
        for _ in range(3):
            v_indices.append(he.vertex.idx)
            he = he.next
        return v_indices

    def trace_ascending_path(self, saddle_edge_id: int) -> List[int]:
        """Traces a gradient path from a saddle upward to a maximum."""
        # A V-path alternates between gradient pairs and boundary relations.
        # ... (Implementation of path tracing)
        return []

    def get_euler_characteristic(self) -> int:
        """Computes the Euler characteristic from critical points."""
        crit = self.get_critical_points()
        return len(crit["minima"]) - len(crit["saddles"]) + len(crit["maxima"])
