from __future__ import annotations
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from typing import List, Tuple, Optional
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.surface.spectral_geometry import SpectralGeometry

class VectorHeatMethod:
    """
    Implements the Vector Heat Method for geodesics and parallel transport.
    Crane et al., "The Heat Method for Distance Substitution", 2013.
    """
    def __init__(self, mesh: SurfaceMesh):
        self.mesh = mesh
        self.num_v = len(mesh.vertices)
        self.L, self.M = SpectralGeometry.compute_laplacian_cotan(mesh)
        
        # Precompute mean edge length for time step t
        avg_len = self._compute_avg_edge_length()
        self.t = avg_len**2
        
    def _compute_avg_edge_length(self) -> float:
        total_len = 0.0
        count = 0
        for face in self.mesh.faces:
            for i in range(len(face)):
                v1 = self.mesh.vertices[face[i]]
                v2 = self.mesh.vertices[face[(i+1)%len(face)]]
                total_len += v1.distance_to(v2)
                count += 1
        return total_len / count if count > 0 else 1.0

    def compute_geodesics(self, source_indices: List[int]) -> np.ndarray:
        """
        Computes the geodesic distance from sources to all vertices.
        """
        # 1. Heat Flow: (M - tL) u = delta
        # Using implicit Euler step
        A = self.M - self.t * self.L
        delta = np.zeros(self.num_v)
        delta[source_indices] = 1.0
        
        u = spsolve(A, delta)
        
        # 2. Gradient Field: X = -grad u / |grad u|
        gradients = self._compute_gradients(u)
        
        # Normalize and negate
        X = -gradients / (np.linalg.norm(gradients, axis=1, keepdims=True) + 1e-10)
        
        # 3. Poisson: L phi = div X
        divX = self._compute_divergence(X)
        phi = spsolve(self.L, divX)
        
        # Normalize: phi - min(phi)
        phi -= np.min(phi)
        return phi

    def _compute_gradients(self, u: np.ndarray) -> np.ndarray:
        """Computes the gradient of scalar field u per face."""
        num_f = len(self.mesh.faces)
        grads = np.zeros((num_f, 3))
        
        vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in self.mesh.vertices])
        
        for f_idx, face in enumerate(self.mesh.faces):
            # Triangle (i, j, k)
            i, j, k = face[0], face[1], face[2]
            vi, vj, vk = vertices[i], vertices[j], vertices[k]
            
            # Normal
            normal = np.cross(vj - vi, vk - vi)
            area2 = np.linalg.norm(normal)
            if area2 < 1e-12: continue
            normal /= area2
            
            # Gradient in triangle
            # grad u = 1/2A * sum_j u_j (n x e_j)
            e_ik = vk - vi
            e_ij = vj - vi
            e_jk = vk - vj
            
            # Vectors opposite to vertices
            vec_i = np.cross(normal, vk - vj)
            vec_j = np.cross(normal, vi - vk)
            vec_k = np.cross(normal, vj - vi)
            
            grads[f_idx] = (u[i] * vec_i + u[j] * vec_j + u[k] * vec_k) / area2
            
        return grads

    def _compute_divergence(self, X: np.ndarray) -> np.ndarray:
        """Computes the divergence of vector field X at each vertex."""
        div = np.zeros(self.num_v)
        vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in self.mesh.vertices])
        
        for f_idx, face in enumerate(self.mesh.faces):
            # Triangle (i, j, k)
            i, j, k = face[0], face[1], face[2]
            vi, vj, vk = vertices[i], vertices[j], vertices[k]
            
            Xi = X[f_idx]
            
            # Contribution to divergence: 1/2 * cot(theta) * dot(X, e) ?
            # Standard discrete divergence: div X at vertex i = 1/2 * sum_j cot(alpha_ij) dot(X, e_ij) + ...
            # Simpler: integrate dot(X, n_edge) over boundary of vertex dual cell
            
            # Using the identity: div X at vertex i = 1/2 * sum_{faces f containing i} dot(X_f, e_opposite_perp)
            e_jk = vk - vj
            e_ki = vi - vk
            e_ij = vj - vi
            
            # Normals to edges pointing towards vertex i
            normal = np.cross(vj - vi, vk - vi)
            n_f = normal / np.linalg.norm(normal)
            
            div[i] += 0.5 * np.dot(Xi, np.cross(n_f, e_jk))
            div[j] += 0.5 * np.dot(Xi, np.cross(n_f, e_ki))
            div[k] += 0.5 * np.dot(Xi, np.cross(n_f, e_ij))
            
        return div
