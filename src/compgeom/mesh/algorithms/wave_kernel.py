"""Wave Kernel Signature (WKS) for multiscale shape description."""
from __future__ import annotations
import numpy as np
from scipy.sparse.linalg import eigsh
from typing import List, Tuple, Optional

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.parameterization_bff import BFFParameterizer

class WaveKernelSignature:
    """
    Implements the Wave Kernel Signature (WKS).
    Aubry et al., "The Wave Kernel Signature: A Quantum Mechanical Approach to Shape Analysis", 2011.
    """
    def __init__(self, mesh: TriMesh, k: int = 100):
        self.mesh = mesh
        self.num_v = len(mesh.vertices)
        self.k = min(k, self.num_v - 1)
        self._compute_eigendecomposition()

    def _compute_eigendecomposition(self):
        """Computes the first k eigenvalues and eigenvectors of the Laplacian."""
        bff = BFFParameterizer(self.mesh)
        L = -bff.L # Positive semi-definite Laplacian
        
        # Mass matrix
        V = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in self.mesh.vertices])
        F = np.array(self.mesh.faces)
        e1 = V[F[:, 1]] - V[F[:, 0]]
        e2 = V[F[:, 2]] - V[F[:, 0]]
        face_areas = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
        vertex_areas = np.zeros(self.num_v)
        for i in range(3):
            np.add.at(vertex_areas, F[:, i], face_areas / 3.0)
        from scipy.sparse import diags
        M = diags(vertex_areas)
        
        # Solve generalized eigenvalue problem: L phi = lambda M phi
        # Add small epsilon to diagonal for stability
        L += diags(np.full(self.num_v, 1e-8))
        
        evals, evecs = eigsh(L, k=self.k, M=M, which='SM')
        self.evals = np.maximum(evals, 1e-12)
        self.evecs = evecs

    def compute(self, num_scales: int = 100, sigma: float = 6.0) -> np.ndarray:
        """
        Computes the WKS for each vertex.
        
        Returns:
            An (N, num_scales) array of signatures.
        """
        log_evals = np.log(self.evals)
        e_min = np.min(log_evals) + 2 * sigma
        e_max = np.max(log_evals) - 2 * sigma
        
        energies = np.linspace(e_min, e_max, num_scales)
        wks = np.zeros((self.num_v, num_scales))
        
        for i, e in enumerate(energies):
            # Gaussian weights in log-space
            weights = np.exp(-(e - log_evals)**2 / (2 * sigma**2))
            # WKS = sum_j phi_j^2 * weights_j
            wks[:, i] = (self.evecs**2) @ weights
            
        # Normalize per vertex
        norms = np.sum(wks, axis=1, keepdims=True)
        wks /= (norms + 1e-12)
        
        return wks
