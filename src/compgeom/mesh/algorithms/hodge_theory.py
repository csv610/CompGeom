"""Helmholtz-Hodge Decomposition for 1-forms on surface meshes."""
from __future__ import annotations
import numpy as np
from scipy.sparse.linalg import spsolve
from typing import List, Tuple, Dict, Optional

from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh
from compgeom.mesh.algorithms.dec import DEC

class HodgeDecomposition:
    """
    Decomposes a discrete 1-form (values on edges) into exact, co-exact, and harmonic components.
    """
    def __init__(self, he_mesh: HalfEdgeMesh):
        self.dec = DEC(he_mesh)
        self.d0 = self.dec.d0()
        self.d1 = self.dec.d1()
        self.s0 = self.dec.star0()
        self.s1 = self.dec.star1()
        self.s2 = self.dec.star2()

    def decompose(self, omega: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Decomposes 1-form omega into (exact, co_exact, harmonic).
        omega = d*phi + delta*psi + h
        
        Args:
            omega: (num_e,) array of 1-form values on primal edges.
            
        Returns:
            (exact, co_exact, harmonic) components, each of shape (num_e,).
        """
        # 1. Exact Part: d * phi
        # Solve: d0^T * s1 * d0 * phi = d0^T * s1 * omega
        L0 = self.d0.T @ self.s1 @ self.d0
        rhs0 = self.d0.T @ self.s1 @ omega
        # Regularize to handle kernel (constant functions)
        from scipy.sparse import eye
        phi = spsolve(L0 + 1e-10 * eye(self.dec.num_v), rhs0)
        exact = self.d0 @ phi
        
        # 2. Co-exact Part: s1^-1 * d1^T * s2 * psi
        # Solve: d1 * s1^-1 * d1^T * s2 * psi = d1 * omega
        # Let s1_inv = inv(s1)
        s1_inv = self.s1.copy()
        s1_inv.data = 1.0 / (s1_inv.data + 1e-12)
        
        L1 = self.d1 @ s1_inv @ self.d1.T @ self.s2
        rhs1 = self.d1 @ omega
        psi = spsolve(L1 + 1e-10 * eye(self.dec.num_f), rhs1)
        co_exact = s1_inv @ self.d1.T @ self.s2 @ psi
        
        # 3. Harmonic Part: h = omega - exact - co_exact
        harmonic = omega - exact - co_exact
        
        return exact, co_exact, harmonic

    def compute_harmonic_basis(self) -> List[np.ndarray]:
        """
        Computes a basis for the space of harmonic 1-forms using tree-cotree decomposition.

        The dimension of harmonic 1-forms is 2*genus (genus = number of handles).
        This implementation uses the tree-cotree method:
        1. Build a spanning tree of primal edges
        2. Build a spanning tree of dual edges (cotree)
        3. Edges not in either tree form a basis for cycles
        4. Solve for harmonic 1-forms on these basis cycles

        Returns:
            List of harmonic 1-forms (each of shape (num_e,)).
        """
        from scipy.sparse import csr_matrix
        from scipy.sparse.linalg import eigsh, spsolve

        # Compute genus from Euler characteristic
        # chi = V - E + F = 2 - 2*genus (for closed orientable surface)
        num_v, num_e, num_f = self.dec.num_v, self.dec.num_e, self.dec.num_f
        euler = num_v - num_e + num_f
        genus = (2 - euler) // 2

        if genus <= 0:
            return []  # No handles (sphere, disk, etc.)

        # Build spanning tree on primal mesh
        tree_edges = self._build_spanning_tree()

        # Build cotree (spanning tree on dual mesh)
        cotree_edges = self._build_cotree()

        # Generator edges: not in tree AND not in cotree
        generator_edges = [i for i in range(num_e)
                          if i not in tree_edges and i not in cotree_edges]

        # We need 2*genus generators
        if len(generator_edges) < 2 * genus:
            return []

        # For each generator, construct a closed 1-form and project to harmonic
        harmonic_forms = []
        for gen_idx in generator_edges[:2 * genus]:
            # Construct 1-form with circulation around this edge
            omega = np.zeros(num_e)
            omega[gen_idx] = 1.0

            # Make it closed (curl-free) by solving for potential
            # Then subtract exact part to get harmonic component
            exact, co_exact, harmonic = self.decompose(omega)

            # Normalize
            norm = np.linalg.norm(harmonic)
            if norm > 1e-10:
                harmonic = harmonic / norm
                harmonic_forms.append(harmonic)

        return harmonic_forms

    def _build_spanning_tree(self) -> set:
        """Build a spanning tree on the primal mesh vertices."""
        n = self.dec.num_v
        tree_edges = set()
        visited = {0}  # Start from vertex 0
        frontier = [(e_idx, 0) for e_idx in range(self.dec.num_e)
                   if self.dec.E_idx[e_idx, 0] == 0 or self.dec.E_idx[e_idx, 1] == 0]

        while len(visited) < n and frontier:
            e_idx, _ = frontier.pop(0)
            u, v = self.dec.E_idx[e_idx]

            if u in visited and v not in visited:
                tree_edges.add(e_idx)
                visited.add(v)
                # Add edges from new vertex
                for e2 in range(self.dec.num_e):
                    u2, v2 = self.dec.E_idx[e2]
                    if v2 == v and u2 in visited:
                        frontier.append((e2, v))
                    elif u2 == v and v2 in visited:
                        frontier.append((e2, v))
            elif v in visited and u not in visited:
                tree_edges.add(e_idx)
                visited.add(u)
                for e2 in range(self.dec.num_e):
                    u2, v2 = self.dec.E_idx[e2]
                    if v2 == u and u2 in visited:
                        frontier.append((e2, u))
                    elif u2 == u and v2 in visited:
                        frontier.append((e2, u))

        return tree_edges

    def _build_cotree(self) -> set:
        """Build a spanning tree on the dual mesh (faces)."""
        tree_edges = set()
        if self.dec.num_f == 0:
            return tree_edges

        visited = {0}  # Start from face 0
        frontier = []

        # Build adjacency for dual mesh (faces connected by edges)
        face_adj = [[] for _ in range(self.dec.num_f)]
        for e_idx, he in enumerate(self.dec.primal_edges):
            if he.face and he.twin and he.twin.face:
                f1, f2 = he.face.idx, he.twin.face.idx
                face_adj[f1].append((e_idx, f2))
                face_adj[f2].append((e_idx, f1))

        # Start BFS
        queue = [0]
        while queue:
            f = queue.pop(0)
            for e_idx, f2 in face_adj[f]:
                if f2 not in visited:
                    tree_edges.add(e_idx)
                    visited.add(f2)
                    queue.append(f2)

        return tree_edges
