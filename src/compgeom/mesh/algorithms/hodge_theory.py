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
        Computes a basis for the space of harmonic 1-forms.
        Dimension should be 2 * genus.
        """
        # This involves finding closed 1-forms that are not exact.
        # Typically done via tree-cotree decomposition.
        # For now, placeholder.
        return []
