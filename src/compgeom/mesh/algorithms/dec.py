"""Discrete Exterior Calculus (DEC) operators for surface meshes."""
from __future__ import annotations
import numpy as np
from scipy.sparse import csr_matrix, diags
from typing import List, Tuple, Dict, Set, Optional

from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh, HalfEdge

class DEC:
    """
    Constructs discrete exterior calculus operators (d, star) for a triangle mesh.
    """
    def __init__(self, he_mesh: HalfEdgeMesh):
        self.he_mesh = he_mesh
        self.num_v = len(he_mesh.vertices)
        self.num_f = len(he_mesh.faces)
        
        # 1. Identify canonical edges and build indices
        self.primal_edges: List[HalfEdge] = []
        self.edge_to_idx: Dict[int, int] = {} # canonical half-edge ID -> primal edge index
        
        for he in he_mesh.edges:
            if not he.twin or he.idx < he.twin.idx:
                self.edge_to_idx[he.idx] = len(self.primal_edges)
                if he.twin:
                    self.edge_to_idx[he.twin.idx] = len(self.primal_edges)
                self.primal_edges.append(he)
        
        self.num_e = len(self.primal_edges)

    def d0(self) -> csr_matrix:
        """Exterior derivative from vertices (0-forms) to edges (1-forms)."""
        rows, cols, data = [], [], []
        for i, he in enumerate(self.primal_edges):
            # d0 maps vertex differences along edges
            # Edge i: v_start -> v_end
            v_start = he.vertex.idx
            v_end = he.next.vertex.idx
            
            # (d0 * f)_i = f(v_end) - f(v_start)
            rows.extend([i, i])
            cols.extend([v_end, v_start])
            data.extend([1.0, -1.0])
            
        return csr_matrix((data, (rows, cols)), shape=(self.num_e, self.num_v))

    def d1(self) -> csr_matrix:
        """Exterior derivative from edges (1-forms) to faces (2-forms)."""
        rows, cols, data = [], [], []
        for i, face in enumerate(self.he_mesh.faces):
            # Boundary of face: sum of oriented edges
            curr = face.edge
            for _ in range(3):
                edge_idx = self.edge_to_idx[curr.idx]
                
                # Check orientation: +1 if canonical, -1 if flipped
                canonical_he = self.primal_edges[edge_idx]
                sign = 1.0 if curr.idx == canonical_he.idx else -1.0
                
                rows.append(i)
                cols.append(edge_idx)
                data.append(sign)
                curr = curr.next
                
        return csr_matrix((data, (rows, cols)), shape=(self.num_f, self.num_e))

    def star0(self) -> csr_matrix:
        """Primal 0-form to dual 2-form (Vertex mass matrix)."""
        # Lumped mass matrix (barycentric areas)
        areas = np.zeros(self.num_v)
        for face in self.he_mesh.faces:
            # Simple area proxy: 1/3 of face area per vertex
            # Actually, let's use the real triangle areas.
            v_indices = []
            curr = face.edge
            for _ in range(3):
                v_indices.append(curr.vertex.point)
                curr = curr.next
            
            p0, p1, p2 = v_indices
            area = self._tri_area(p0, p1, p2)
            for curr in [face.edge, face.edge.next, face.edge.next.next]:
                areas[curr.vertex.idx] += area / 3.0
                
        return diags(areas)

    def star1(self) -> csr_matrix:
        """Primal 1-form to dual 1-form (Cotangent weights)."""
        weights = np.zeros(self.num_e)
        for i, he in enumerate(self.primal_edges):
            # Discrete Hodge star for edges: 0.5 * (cot(alpha) + cot(beta))
            w = self._cotan_weight(he)
            if he.twin:
                w += self._cotan_weight(he.twin)
            weights[i] = w * 0.5
            
        return diags(weights)

    def star2(self) -> csr_matrix:
        """Primal 2-form to dual 0-form (Inverse face areas)."""
        inv_areas = []
        for face in self.he_mesh.faces:
            pts = []
            curr = face.edge
            for _ in range(3):
                pts.append(curr.vertex.point)
                curr = curr.next
            area = self._tri_area(pts[0], pts[1], pts[2])
            inv_areas.append(1.0 / area if area > 1e-12 else 0.0)
            
        return diags(inv_areas)

    def _tri_area(self, p0, p1, p2) -> float:
        ux, uy, uz = p1.x - p0.x, p1.y - p0.y, getattr(p1, 'z', 0.0) - getattr(p0, 'z', 0.0)
        vx, vy, vz = p2.x - p0.x, p2.y - p0.y, getattr(p2, 'z', 0.0) - getattr(p0, 'z', 0.0)
        return 0.5 * np.sqrt((uy*vz - uz*vy)**2 + (uz*vx - ux*vz)**2 + (ux*vy - uy*vx)**2)

    def _cotan_weight(self, he: HalfEdge) -> float:
        # Angle at the vertex opposite to 'he' in its face
        # Vertices: he.vertex, he.next.vertex, he.next.next.vertex
        # Opposite vertex is he.next.next.vertex
        p_opp = he.next.next.vertex.point
        p1 = he.vertex.point
        p2 = he.next.vertex.point
        
        v1 = np.array([p1.x - p_opp.x, p1.y - p_opp.y, getattr(p1, 'z', 0.0) - getattr(p_opp, 'z', 0.0)])
        v2 = np.array([p2.x - p_opp.x, p2.y - p_opp.y, getattr(p2, 'z', 0.0) - getattr(p_opp, 'z', 0.0)])
        
        dot = np.dot(v1, v2)
        cross = np.linalg.norm(np.cross(v1, v2))
        return dot / (cross + 1e-12)
