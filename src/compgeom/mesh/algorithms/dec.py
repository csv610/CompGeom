"""Discrete Exterior Calculus (DEC) operators for surface meshes."""
from __future__ import annotations
import numpy as np
from scipy.sparse import csr_matrix, diags
from typing import List, Tuple, Dict, Set, Optional

from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh, HalfEdge

class DEC:
    """
    Constructs discrete exterior calculus operators (d, star) for a triangle mesh.
    Uses fully vectorized NumPy operations for industrial performance.
    """
    def __init__(self, he_mesh: HalfEdgeMesh):
        self.he_mesh = he_mesh
        self.num_v = len(he_mesh.vertices)
        self.num_f = len(he_mesh.faces)
        
        # 1. Geometry Data
        self.V = np.array([[v.point.x, v.point.y, getattr(v.point, 'z', 0.0)] for v in he_mesh.vertices])
        self.F = np.array([[he.vertex.idx for he in [f.edge, f.edge.next, f.edge.next.next]] for f in he_mesh.faces])
        
        # 2. Canonical Edges
        self.primal_edges: List[HalfEdge] = []
        self.edge_to_idx: Dict[int, int] = {}
        for he in he_mesh.edges:
            if not he.twin or he.idx < he.twin.idx:
                self.edge_to_idx[he.idx] = len(self.primal_edges)
                if he.twin: self.edge_to_idx[he.twin.idx] = len(self.primal_edges)
                self.primal_edges.append(he)
        self.num_e = len(self.primal_edges)
        
        # Precompute edge data
        self.E_idx = np.array([[he.vertex.idx, he.next.vertex.idx] for he in self.primal_edges])

    def d0(self) -> csr_matrix:
        """Exterior derivative from vertices to edges."""
        I = np.arange(self.num_e)
        rows = np.concatenate([I, I])
        cols = np.concatenate([self.E_idx[:, 1], self.E_idx[:, 0]])
        data = np.concatenate([np.ones(self.num_e), -np.ones(self.num_e)])
        return csr_matrix((data, (rows, cols)), shape=(self.num_e, self.num_v))

    def d1(self) -> csr_matrix:
        """Exterior derivative from edges to faces."""
        rows, cols, data = [], [], []
        for i, face in enumerate(self.he_mesh.faces):
            curr = face.edge
            for _ in range(3):
                e_idx = self.edge_to_idx[curr.idx]
                sign = 1.0 if curr.idx == self.primal_edges[e_idx].idx else -1.0
                rows.append(i); cols.append(e_idx); data.append(sign)
                curr = curr.next
        return csr_matrix((data, (rows, cols)), shape=(self.num_f, self.num_e))

    def star0(self) -> csr_matrix:
        """Lumped mass matrix (Vertex areas)."""
        # Vectorized area calculation
        e1 = self.V[self.F[:, 1]] - self.V[self.F[:, 0]]
        e2 = self.V[self.F[:, 2]] - self.V[self.F[:, 0]]
        face_areas = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
        
        vertex_areas = np.zeros(self.num_v)
        for i in range(3):
            np.add.at(vertex_areas, self.F[:, i], face_areas / 3.0)
        return diags(vertex_areas)

    def star1(self) -> csr_matrix:
        """Primal 1-form to dual 1-form (Cotangent weights)."""
        # Edge-wise cotangent weights
        weights = np.zeros(self.num_e)
        
        # Vectorized per-face cotangents
        for i in range(3):
            v0 = self.F[:, i]
            v1 = self.F[:, (i+1)%3]
            v2 = self.F[:, (i+2)%3]
            
            # Edges opposite to v0, v1, v2
            # Edge i is v1 -> v2
            vec1 = self.V[v1] - self.V[v0]
            vec2 = self.V[v2] - self.V[v0]
            
            dot = np.einsum('ij,ij->i', vec1, vec2)
            cross = np.linalg.norm(np.cross(vec1, vec2), axis=1)
            cot = dot / (cross + 1e-12)
            
            # Map face-local cotangent to the edge opposite to v0 (the i-th edge of the face)
            for f_idx, face in enumerate(self.he_mesh.faces):
                # The edge opposite to v0 is face.edge.next (if face.edge starts at v0)
                # Let's find the correct half-edge
                he = face.edge
                for _ in range(i): he = he.next # Rotate to vertex i
                target_he = he.next # Edge opposite to vertex i
                e_idx = self.edge_to_idx[target_he.idx]
                weights[e_idx] += cot[f_idx] * 0.5
                
        return diags(weights)

    def star2(self) -> csr_matrix:
        """Primal 2-form to dual 0-form (Inverse face areas)."""
        e1 = self.V[self.F[:, 1]] - self.V[self.F[:, 0]]
        e2 = self.V[self.F[:, 2]] - self.V[self.F[:, 0]]
        face_areas = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
        return diags(1.0 / (face_areas + 1e-12))
