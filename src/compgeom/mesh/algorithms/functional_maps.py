"""Functional Maps for finding correspondences between surface meshes."""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
from typing import List, Tuple, Optional

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.wave_kernel import WaveKernelSignature

class FunctionalMap:
    """
    Implements the Functional Maps framework for shape matching.
    Ovsjanikov et al., "Functional Maps: A Flexible Representation of Maps between Shapes", SIGGRAPH 2012.
    """
    def __init__(self, mesh1: TriMesh, mesh2: TriMesh, k: int = 30):
        self.mesh1 = mesh1
        self.mesh2 = mesh2
        self.k = k
        self._compute_bases()

    def _compute_bases(self):
        """Computes Laplacian eigenfunctions for both meshes."""
        wks1 = WaveKernelSignature(self.mesh1, k=self.k)
        wks2 = WaveKernelSignature(self.mesh2, k=self.k)
        
        self.evals1, self.evecs1 = wks1.evals, wks1.evecs
        self.evals2, self.evecs2 = wks2.evals, wks2.evecs
        
        # Descriptors (using WKS)
        self.desc1 = wks1.compute(num_scales=50)
        self.desc2 = wks2.compute(num_scales=50)

    def compute_map(self) -> np.ndarray:
        """
        Solves for the functional map matrix C (k x k).
        C matches descriptors: C * coefficients1 = coefficients2
        """
        # 1. Project descriptors onto bases
        # A = Phi_1^+ * desc1, B = Phi_2^+ * desc2
        A = np.linalg.pinv(self.evecs1) @ self.desc1
        B = np.linalg.pinv(self.evecs2) @ self.desc2
        
        # 2. Solve for C: min ||CA - B||^2
        # C = B * A^T * (A * A^T)^-1
        C = B @ np.linalg.pinv(A)
        
        return C

    def vertex_correspondence(self, C: np.ndarray) -> np.ndarray:
        """
        Converts the functional map C to a vertex-to-vertex map.
        
        Returns:
            An array of indices 'map' such that mesh1 vertex i maps to mesh2 vertex map[i].
        """
        # Map eigenvectors from mesh1 to mesh2 space: Phi_1_mapped = Phi_2 * C
        # Then for each vertex in mesh1, find the nearest vertex in mesh2 based on spectral coords.
        evecs1_mapped = self.evecs1 @ C.T
        
        # Spectral embedding of mesh2
        spectral2 = self.evecs2
        
        # Nearest neighbor search in spectral space
        from scipy.spatial import cKDTree
        tree = cKDTree(spectral2)
        _, indices = tree.query(evecs1_mapped)
        
        return indices
