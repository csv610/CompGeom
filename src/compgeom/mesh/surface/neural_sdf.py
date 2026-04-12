from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
from typing import List, Tuple, Callable
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.volume.marching_cubes import MarchingCubes

class TinyNeuralSDF:
    """
    A minimalist Neural SDF implementation using a NumPy-based MLP.
    Optimized using SciPy's L-BFGS-B to fit a point cloud.
    """
    def __init__(self, hidden_dim: int = 32):
        # 3 (input) -> hidden -> hidden -> 1 (output SDF)
        self.dims = [3, hidden_dim, hidden_dim, 1]
        self.params = self._init_params()
        
    def _init_params(self) -> np.ndarray:
        p = []
        for i in range(len(self.dims) - 1):
            # He initialization
            w = np.random.randn(self.dims[i], self.dims[i+1]) * np.sqrt(2.0 / self.dims[i])
            b = np.zeros(self.dims[i+1])
            p.extend(w.flatten())
            p.extend(b.flatten())
        return np.array(p)

    def _unpack(self, p: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        weights_biases = []
        cursor = 0
        for i in range(len(self.dims) - 1):
            w_size = self.dims[i] * self.dims[i+1]
            b_size = self.dims[i+1]
            w = p[cursor : cursor + w_size].reshape(self.dims[i], self.dims[i+1])
            cursor += w_size
            b = p[cursor : cursor + b_size]
            cursor += b_size
            weights_biases.append((w, b))
        return weights_biases

    def forward(self, x: np.ndarray, params: np.ndarray = None) -> np.ndarray:
        """Forward pass: (N, 3) -> (N, 1)."""
        wb = self._unpack(params if params is not None else self.params)
        curr = x
        for i, (w, b) in enumerate(wb):
            curr = curr @ w + b
            if i < len(wb) - 1:
                # Softplus activation for smooth SDF
                curr = np.log(1 + np.exp(np.clip(curr, -20, 20)))
        return curr

    def fit(self, points: List[Point3D], iterations: int = 200):
        """Fits the neural SDF to a point cloud using L-BFGS."""
        target_pts = np.array([[p.x, p.y, p.z] for p in points])
        self.bbox_min = np.min(target_pts, axis=0) - 0.1
        self.bbox_max = np.max(target_pts, axis=0) + 0.1
        
        def loss_fn(p):
            # 1. Surface loss: f(p) = 0
            sdf_surf = self.forward(target_pts, p)
            loss_surf = np.mean(sdf_surf**2)
            
            # 2. Approximate Eikonal loss: |f(p)| should be approx distance to surface
            # We use a simple "push" away from the surface for off-surface points
            rand_pts = np.random.uniform(self.bbox_min, self.bbox_max, (len(target_pts), 3))
            sdf_rand = self.forward(rand_pts, p)
            # Loss: sum of (sdf_rand - dist_to_surface)^2
            # Since computing exact distance is slow, we just penalize near-zero values off-surface
            loss_off = np.mean(np.exp(-np.abs(sdf_rand) * 10)) 
            
            return loss_surf + 0.1 * loss_off

        res = minimize(loss_fn, self.params, method='L-BFGS-B', options={'maxiter': iterations})
        self.params = res.x

    def to_mesh(self, res: int = 32) -> TriMesh:
        """Extracts the isosurface using Marching Cubes."""
        def scalar_field(x, y, z):
            pts = np.array([[x, y, z]])
            return self.forward(pts)[0, 0]

        return MarchingCubes.reconstruct(scalar_field, tuple(self.bbox_min), tuple(self.bbox_max), resolution=res, isovalue=0.0)

    def to_mesh_tetra(self, res: int = 32) -> TriMesh:
        """Extracts the isosurface using Marching Tetrahedra."""
        from compgeom.mesh.volume.marching_tetrahedra import MarchingTetrahedra
        def scalar_field(x, y, z):
            pts = np.array([[x, y, z]])
            return self.forward(pts)[0, 0]

        return MarchingTetrahedra.from_implicit(scalar_field, tuple(self.bbox_min), tuple(self.bbox_max), resolution=res, isovalue=0.0)
