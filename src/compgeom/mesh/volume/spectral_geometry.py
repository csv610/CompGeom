from __future__ import annotations
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
from typing import List, Tuple, Optional
from compgeom.mesh.surface.surface_mesh import SurfaceMesh

class SpectralGeometry:
    """
    Algorithms for spectral analysis of meshes using the Laplace-Beltrami operator.
    """
    @staticmethod
    def compute_laplacian_cotan(mesh: SurfaceMesh) -> Tuple[sparse.csc_matrix, sparse.csc_matrix]:
        """
        Computes the Cotangent Laplacian matrix (L) and the diagonal Mass matrix (M).
        L is the stiffness matrix, M is the area weights.
        """
        num_v = len(mesh.vertices)
        rows, cols, data = [], [], []
        mass_data = np.zeros(num_v)
        
        vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        
        for face in mesh.faces:
            # For each triangle (i, j, k)
            for a, b, c in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
                i, j, k = face[a], face[b], face[c]
                
                vi, vj, vk = vertices[i], vertices[j], vertices[k]
                
                # Vectors
                e1 = vi - vk
                e2 = vj - vk
                
                # Cotangent of angle at k
                # cot = (e1 . e2) / |e1 x e2|
                cross_prod = np.cross(e1, e2)
                area2 = np.linalg.norm(cross_prod)
                if area2 < 1e-12: continue
                
                cot = np.dot(e1, e2) / area2
                weight = 0.5 * cot
                
                # Stiffness matrix L
                rows.extend([i, j, i, j])
                cols.extend([j, i, i, j])
                data.extend([-weight, -weight, weight, weight])
                
                # Mass matrix M (Barycentric area)
                mass_data[i] += area2 / 6.0
                mass_data[j] += area2 / 6.0
                mass_data[k] += area2 / 6.0
                
        L = sparse.csc_matrix((data, (rows, cols)), shape=(num_v, num_v))
        M = sparse.diags(mass_data).tocsc()
        return L, M

    @staticmethod
    def compute_eigenstructures(mesh: SurfaceMesh, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the first k eigenvalues and eigenvectors of the Laplace-Beltrami operator.
        Solves L x = lambda M x.
        """
        L, M = SpectralGeometry.compute_laplacian_cotan(mesh)
        
        # We use shift-invert mode to find the smallest eigenvalues.
        # sigma is the target value. Since the smallest is 0, we target 0.
        # We add a small epsilon to avoid singularity during LU decomposition in eigsh.
        eigenvalues, eigenvectors = eigsh(L, k=min(k, L.shape[0]-1), M=M, which='LM', sigma=-1e-8)
        
        # Ensure they are sorted
        idx = np.argsort(eigenvalues)
        return eigenvalues[idx], eigenvectors[:, idx]

    @staticmethod
    def compute_hks(mesh: SurfaceMesh, timestamps: np.ndarray, k: int = 100) -> np.ndarray:
        """
        Computes the Heat Kernel Signature (HKS) for each vertex.
        timestamps: time values t to evaluate the heat kernel.
        Returns array of shape (num_vertices, len(timestamps)).
        """
        evals, evecs = SpectralGeometry.compute_eigenstructures(mesh, k=k)
        
        # HKS(x, t) = sum_j exp(-lambda_j * t) * phi_j(x)^2
        hks = np.zeros((len(mesh.vertices), len(timestamps)))
        
        for i, t in enumerate(timestamps):
            weights = np.exp(-evals * t)
            hks[:, i] = (evecs**2) @ weights
            
        # Normalize HKS for scale invariance
        hks /= np.sum(hks, axis=1, keepdims=True)
        return hks

    @staticmethod
    def compute_diffusion_embedding(mesh: SurfaceMesh, t: float, k: int = 100) -> np.ndarray:
        """
        Computes the diffusion embedding at time t.
        The Euclidean distance in this embedding space is the diffusion distance.
        Returns array of shape (num_vertices, k).
        """
        evals, evecs = SpectralGeometry.compute_eigenstructures(mesh, k=k)
        # Coordinates: exp(-lambda_j * t) * phi_j(x)
        embedding = evecs * np.exp(-evals * t)
        return embedding

    @staticmethod
    def compute_diffusion_distance(mesh: SurfaceMesh, i: int, j: int, t: float, k: int = 100) -> float:
        """
        Computes the diffusion distance between vertex i and vertex j at time t.
        """
        emb = SpectralGeometry.compute_diffusion_embedding(mesh, t, k)
        return float(np.linalg.norm(emb[i] - emb[j]))
