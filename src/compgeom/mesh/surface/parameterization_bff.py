"""
Boundary First Flattening (BFF, 2017) for robust conformal parameterization.
Keenan Crane, "Boundary First Flattening", SIGGRAPH 2017.
"""

from __future__ import annotations
import math
import numpy as np
from collections import defaultdict
from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import spsolve
from typing import List, Tuple, Dict, Set, Optional

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point2D, Point3D

class BFFParameterizer:
    """
    Implements Boundary First Flattening for conformal mesh flattening.
    Unlike Harmonic Mapping, BFF allows prescribing the target boundary curvature.
    """
    def __init__(self, mesh: TriMesh):
        self.mesh = mesh
        self.num_v = len(mesh.vertices)
        self._build_laplacian()

    def _build_laplacian(self):
        """Builds the cotangent Laplacian matrix L."""
        V = np.array([[v.x, v.y, v.z] for v in self.mesh.vertices])
        F = np.array(self.mesh.faces)
        
        # 1. Compute half-edge vectors
        # e0 = f1 - f2, e1 = f2 - f0, e2 = f0 - f1
        e0 = V[F[:, 2]] - V[F[:, 1]]
        e1 = V[F[:, 0]] - V[F[:, 2]]
        e2 = V[F[:, 1]] - V[F[:, 0]]
        
        # 2. Compute face areas
        cross = np.cross(e0, e1)
        areas = 0.5 * np.linalg.norm(cross, axis=1)
        
        # 3. Compute cotangents
        cot0 = -np.einsum('ij,ij->i', e1, e2) / (4.0 * areas)
        cot1 = -np.einsum('ij,ij->i', e2, e0) / (4.0 * areas)
        cot2 = -np.einsum('ij,ij->i', e0, e1) / (4.0 * areas)
        
        # 4. Fill Laplacian matrix
        I = np.concatenate([F[:, 1], F[:, 2], F[:, 2], F[:, 0], F[:, 0], F[:, 1]])
        J = np.concatenate([F[:, 2], F[:, 1], F[:, 0], F[:, 2], F[:, 1], F[:, 0]])
        W = np.concatenate([cot0, cot0, cot1, cot1, cot2, cot2])
        
        L = csr_matrix((W, (I, J)), shape=(self.num_v, self.num_v))
        diag = -np.array(L.sum(axis=1)).flatten()
        L = L + csr_matrix((diag, (range(self.num_v), range(self.num_v))), shape=(self.num_v, self.num_v))
        
        self.L = L

    def flatten_to_disk(self) -> List[Point2D]:
        """
        Flattens the mesh to a disk by prescribing a constant boundary curvature.
        This is the most common use-case for BFF.
        """
        # 1. Find boundary loop
        boundary_v = self._get_boundary_loop()
        n_b = len(boundary_v)
        
        # 2. Prescribe target boundary curvature (kappa_target = 2pi / L_total for disk)
        # For a simple disk, we want a constant geodesic curvature on the boundary.
        # Sum of curvature must be 2*pi (Gauss-Bonnet).
        target_kappa = np.full(n_b, 2.0 * math.pi / n_b)
        
        # 3. Solve for scale factors 'u' on the boundary
        u = self._solve_boundary_system(boundary_v, target_kappa)
        
        # 4. Solve for interior scale factors 'u' via Dirichlet problem
        u_full = self._extend_to_interior(boundary_v, u)
        
        # 5. Integrate flattened boundary positions from 'u' and 'kappa_target'
        # This gives the boundary coordinates in 2D
        # For BFF, we typically use the Integrated Lengths approach.
        uv_boundary = self._integrate_boundary(boundary_v, u, target_kappa)
        
        # 6. Extend boundary UVs to interior via Harmonic Map
        return self._harmonic_extend(boundary_v, uv_boundary)

    def _get_boundary_loop(self) -> List[int]:
        """Identifies the indices of vertices on the boundary."""
        edge_counts = defaultdict(int)
        for f in self.mesh.faces:
            for i in range(3):
                e = tuple(sorted((f[i], f[(i+1)%3])))
                edge_counts[e] += 1
        
        boundary_edges = [e for e, c in edge_counts.items() if c == 1]
        if not boundary_edges:
            raise ValueError("Mesh must have a boundary.")
            
        # Chain edges into a loop
        adj = defaultdict(list)
        for u, v in boundary_edges:
            adj[u].append(v)
            adj[v].append(u)
            
        loop = []
        curr = boundary_edges[0][0]
        prev = -1
        while True:
            loop.append(curr)
            next_v = adj[curr][0] if adj[curr][0] != prev else adj[curr][1]
            if next_v == loop[0]:
                break
            prev = curr
            curr = next_v
        return loop

    def _solve_boundary_system(self, boundary_v: List[int], target_kappa: np.ndarray) -> np.ndarray:
        """
        Solves for boundary scale factors u that achieve target curvature.

        In Boundary First Flattening, we solve:
        h = target_kappa - current_kappa (curvature discrepancy)
        u = G^T * h  (where G is the boundary Green's function)

        For a practical implementation, we use the relationship:
        u minimizes the Dirichlet energy while achieving the target curvature.
        """
        n_b = len(boundary_v)

        # Compute current boundary curvature
        current_kappa = self._compute_boundary_curvature(boundary_v)

        # Curvature discrepancy
        h = target_kappa - current_kappa

        # Ensure mean zero (compatibility condition)
        h = h - np.mean(h)

        # Solve for u using the Laplacian restricted to boundary
        # This is equivalent to finding the potential whose normal derivative
        # gives the desired curvature change

        # Extract boundary-boundary block of Laplacian
        L_bb = self.L[boundary_v, :][:, boundary_v].toarray()

        # Add regularization for numerical stability
        L_reg = L_bb + 1e-10 * np.eye(n_b)

        # The scale factor is approximately the solution to:
        # L_bb * u ≈ h (with proper weighting)
        # We solve using least squares with pseudoinverse
        try:
            u = np.linalg.lstsq(L_reg, h, rcond=1e-10)[0]
        except np.linalg.LinAlgError:
            u = np.zeros(n_b)

        # Normalize to have zero mean (absolute scale doesn't matter)
        u = u - np.mean(u)

        return u

    def _compute_boundary_curvature(self, boundary_v: List[int]) -> np.ndarray:
        """Compute the current discrete geodesic curvature at boundary vertices."""
        n_b = len(boundary_v)
        V = np.array([[v.x, v.y, v.z] for v in self.mesh.vertices])
        kappa = np.zeros(n_b)

        for i in range(n_b):
            prev_idx = boundary_v[(i - 1) % n_b]
            curr_idx = boundary_v[i]
            next_idx = boundary_v[(i + 1) % n_b]

            v_prev = V[prev_idx]
            v_curr = V[curr_idx]
            v_next = V[next_idx]

            # Edge vectors (pointing toward current vertex)
            e1 = v_prev - v_curr
            e2 = v_next - v_curr

            # Normalize
            len1 = np.linalg.norm(e1)
            len2 = np.linalg.norm(e2)

            if len1 > 1e-10 and len2 > 1e-10:
                e1 = e1 / len1
                e2 = e2 / len2

                # Interior angle at boundary vertex
                cos_angle = np.clip(np.dot(e1, e2), -1.0, 1.0)
                angle = np.arccos(cos_angle)

                # Geodesic curvature: π - interior_angle
                kappa[i] = np.pi - angle

        return kappa

    def _extend_to_interior(self, boundary_v: List[int], u_b: np.ndarray) -> np.ndarray:
        """Solves the Dirichlet problem to find interior scale factors."""
        num_v = self.num_v
        boundary_set = set(boundary_v)
        interior_v = [i for i in range(num_v) if i not in boundary_set]
        
        if not interior_v:
            return u_b
            
        # L_ii * u_i = -L_ib * u_b
        L_ii = self.L[interior_v, :][:, interior_v]
        L_ib = self.L[interior_v, :][:, boundary_v]
        
        rhs = -L_ib @ u_b
        u_int = spsolve(L_ii, rhs)
        
        u_full = np.zeros(num_v)
        u_full[boundary_v] = u_b
        u_full[interior_v] = u_int
        return u_full

    def _integrate_boundary(self, boundary_v: List[int], u: np.ndarray, kappa: np.ndarray) -> np.ndarray:
        """Integrates the boundary coordinates from scale factors and curvature."""
        n_b = len(boundary_v)
        # Compute discrete edge lengths in flattened space
        # l_flat = l_orig * exp((u_i + u_j)/2)
        V = np.array([[v.x, v.y, v.z] for v in self.mesh.vertices])
        
        uv = np.zeros((n_b, 2))
        angle = 0.0
        for i in range(n_b):
            j = (i + 1) % n_b
            # Original edge length
            l_orig = np.linalg.norm(V[boundary_v[i]] - V[boundary_v[j]])
            # Flattened edge length
            l_flat = l_orig * math.exp((u[i] + u[j]) / 2.0)
            
            uv[j] = uv[i] + l_flat * np.array([math.cos(angle), math.sin(angle)])
            angle += kappa[j]
            
        return uv

    def _harmonic_extend(self, boundary_v: List[int], uv_b: np.ndarray) -> List[Point2D]:
        """Extends boundary UV coordinates to the interior via Harmonic Mapping."""
        num_v = self.num_v
        boundary_set = set(boundary_v)
        interior_v = [i for i in range(num_v) if i not in boundary_set]
        
        uv_full = np.zeros((num_v, 2))
        uv_full[boundary_v] = uv_b
        
        if interior_v:
            L_ii = self.L[interior_v, :][:, interior_v]
            L_ib = self.L[interior_v, :][:, boundary_v]
            
            ux_int = spsolve(L_ii, -L_ib @ uv_b[:, 0])
            uy_int = spsolve(L_ii, -L_ib @ uv_b[:, 1])
            
            uv_full[interior_v, 0] = ux_int
            uv_full[interior_v, 1] = uy_int
            
        return [Point2D(p[0], p[1]) for p in uv_full]
