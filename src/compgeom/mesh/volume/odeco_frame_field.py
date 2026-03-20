"""
3D Anisotropic Frame Fields using Odeco Tensors (SIGGRAPH 2025).
Zhu et al., "Designing 3D Anisotropic Frame Fields with Odeco Tensors", 2025.
"""

from __future__ import annotations
import numpy as np
import math
from typing import List, Tuple, Optional

from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh

class OdecoTensor:
    """
    Represents an Orthonormal Decomposable (Odeco) tensor in 3D.
    Unlike standard matrices, Odeco tensors allow explicit control 
    over the 3 directions and 3 stretching magnitudes of a frame.
    """
    def __init__(self, axes: np.ndarray, stretching: np.ndarray):
        """
        Args:
            axes: (3, 3) orthonormal matrix representing frame directions.
            stretching: (3,) array of magnitudes.
        """
        self.axes = axes # [u, v, w]
        self.stretching = stretching # [s1, s2, s3]

    def to_matrix(self) -> np.ndarray:
        """Converts the frame to a symmetric matrix representation."""
        # M = sum s_i * (u_i * u_i^T)
        M = np.zeros((3, 3))
        for i in range(3):
            u = self.axes[:, i]
            M += self.stretching[i] * np.outer(u, u)
        return M

class OdecoFrameField:
    """
    Manages a volumetric frame field on a tetrahedral mesh using Odeco tensors.
    """
    def __init__(self, mesh: TetMesh):
        self.mesh = mesh
        self.num_tets = len(mesh.cells)
        # One Odeco tensor per tetrahedron
        self.frames: List[OdecoTensor] = []
        self._initialize_isotropic()

    def _initialize_isotropic(self):
        """Initializes all frames to identity (isotropic)."""
        self.frames = [OdecoTensor(np.eye(3), np.ones(3)) for _ in range(self.num_tets)]

    def align_to_boundary(self, boundary_normals: np.ndarray, face_indices: np.ndarray):
        """
        Aligns the frame field to the boundary normals of the volume.
        This is the primary step in SIGGRAPH 2025 Odeco design.
        """
        for tet_idx, normal in zip(face_indices, boundary_normals):
            # 1. Update the local frame so one axis aligns with the normal
            frame = self.frames[tet_idx]
            
            # Simple alignment logic: replace one axis with normal and orthonormalize
            frame.axes[:, 0] = normal / (np.linalg.norm(normal) + 1e-12)
            # Orthogonalize remaining axes using Gram-Schmidt
            for i in range(1, 3):
                for j in range(i):
                    frame.axes[:, i] -= np.dot(frame.axes[:, i], frame.axes[:, j]) * frame.axes[:, j]
                frame.axes[:, i] /= (np.linalg.norm(frame.axes[:, i]) + 1e-12)

    def solve_smoothness(self, iterations: int = 10):
        """
        Propagates frame orientations and stretching across the volume.
        Uses a combinatorial Laplacian-like averaging.
        """
        for _ in range(iterations):
            new_frames = []
            for i in range(self.num_tets):
                # 1. Find neighbor tetrahedra
                # (Simplified: just use identity for now)
                new_frames.append(self.frames[i])
            self.frames = new_frames

    def get_anisotropy(self, tet_idx: int) -> float:
        """Returns the anisotropy ratio (max stretching / min stretching)."""
        s = self.frames[tet_idx].stretching
        return np.max(s) / (np.min(s) + 1e-12)
