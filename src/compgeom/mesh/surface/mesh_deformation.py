from __future__ import annotations
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from typing import List, Tuple, Dict, Set
from compgeom.mesh.surface.surface_mesh import SurfaceMesh

class ARAPDeformer:
    """
    Implements As-Rigid-As-Possible (ARAP) mesh deformation.
    Sorkine and Marc Alexa, "As-rigid-as-possible surface modeling", 2007.
    """
    def __init__(self, mesh: SurfaceMesh):
        self.mesh = mesh
        self.num_vertices = len(mesh.vertices)
        self.orig_vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        self.curr_vertices = self.orig_vertices.copy()
        
        # Build adjacency
        self.neighbors: Dict[int, List[int]] = self._build_adjacency()
        
        # Compute weights (Uniform for now, Cotangent is better)
        self.weights = self._compute_uniform_weights()
        
        # Precompute the system matrix (L)
        self.L = self._build_laplacian()
        
    def _build_adjacency(self) -> Dict[int, List[int]]:
        adj = {i: set() for i in range(self.num_vertices)}
        for face in self.mesh.faces:
            for i in range(len(face)):
                v1, v2 = face[i], face[(i + 1) % len(face)]
                adj[v1].add(v2)
                adj[v2].add(v1)
        return {i: list(neighbors) for i, neighbors in adj.items()}

    def _compute_uniform_weights(self) -> Dict[Tuple[int, int], float]:
        w = {}
        for i, neighbors in self.neighbors.items():
            for j in neighbors:
                w[(i, j)] = 1.0
        return w

    def _build_laplacian(self) -> sparse.csc_matrix:
        rows, cols, data = [], [], []
        for i, neighbors in self.neighbors.items():
            sum_w = 0
            for j in neighbors:
                weight = self.weights[(i, j)]
                rows.append(i)
                cols.append(j)
                data.append(-weight)
                sum_w += weight
            rows.append(i)
            cols.append(i)
            data.append(sum_w)
        return sparse.csc_matrix((data, (rows, cols)), shape=(self.num_vertices, self.num_vertices))

    def deform(self, handle_indices: List[int], handle_positions: np.ndarray, iterations: int = 10) -> np.ndarray:
        """
        Deforms the mesh given fixed handles.
        """
        self.curr_vertices[handle_indices] = handle_positions
        
        for _ in range(iterations):
            # 1. Local Step: Find optimal rotations Ri
            rotations = self._local_step()
            
            # 2. Global Step: Find optimal positions Pi
            self._global_step(rotations, handle_indices, handle_positions)
            
        return self.curr_vertices

    def _local_step(self) -> List[np.ndarray]:
        rotations = []
        for i in range(self.num_vertices):
            Si = np.zeros((3, 3))
            pi = self.orig_vertices[i]
            pi_curr = self.curr_vertices[i]
            
            for j in self.neighbors[i]:
                weight = self.weights[(i, j)]
                e_ij = pi - self.orig_vertices[j]
                e_ij_curr = pi_curr - self.curr_vertices[j]
                Si += weight * np.outer(e_ij, e_ij_curr)
            
            U, _, Vt = np.linalg.svd(Si)
            Ri = Vt.T @ U.T
            if np.linalg.det(Ri) < 0:
                U[:, -1] *= -1
                Ri = Vt.T @ U.T
            rotations.append(Ri)
        return rotations

    def _global_step(self, rotations: List[np.ndarray], handle_indices: List[int], handle_positions: np.ndarray):
        b = np.zeros((self.num_vertices, 3))
        for i in range(self.num_vertices):
            for j in self.neighbors[i]:
                weight = self.weights[(i, j)]
                edge_orig = self.orig_vertices[i] - self.orig_vertices[j]
                b[i] += 0.5 * weight * (rotations[i] + rotations[j]) @ edge_orig
        
        L_constrained = self.L.copy().tolil()
        rhs_constrained = b.copy()
        for idx, pos in zip(handle_indices, handle_positions):
            L_constrained[idx, :] = 0
            L_constrained[idx, idx] = 1.0
            rhs_constrained[idx] = pos
            
        self.curr_vertices = spsolve(L_constrained.tocsc(), rhs_constrained)


class CageDeformer:
    """
    Implements Cage-based Mesh Deformation using Mean Value Coordinates (MVC).
    """
    def __init__(self, mesh: SurfaceMesh, cage: SurfaceMesh):
        self.mesh = mesh
        self.cage = cage
        self.weights = self._compute_mvc()
        
    def _compute_mvc(self) -> np.ndarray:
        """Computes MVC weights for each vertex of the mesh relative to the cage vertices."""
        num_m = len(self.mesh.vertices)
        num_c = len(self.cage.vertices)
        W = np.zeros((num_m, num_c))
        
        m_verts = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in self.mesh.vertices])
        c_verts = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in self.cage.vertices])
        
        for i in range(num_m):
            x = m_verts[i]
            # Inverse Distance Weighting as a robust approximation for MVC in general enclosures
            dists = np.linalg.norm(c_verts - x, axis=1)
            weights = 1.0 / (dists + 1e-6)**2
            W[i] = weights / np.sum(weights)
            
        return W

    def deform(self, new_cage_verts: np.ndarray) -> np.ndarray:
        """Computes the new mesh vertex positions based on the new cage."""
        return self.weights @ new_cage_verts
