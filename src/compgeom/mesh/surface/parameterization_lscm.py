"""Least Squares Conformal Maps (LSCM) for fast mesh parameterization."""
from __future__ import annotations
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import spsolve
from typing import List, Tuple, Optional

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point2D

class LSCMParameterizer:
    """
    Implements Least Squares Conformal Maps (LSCM).
    L\u00e9vy et al., "Least Squares Conformal Maps for Automatic Texture Atlas Generation", SIGGRAPH 2002.
    """
    def __init__(self, mesh: TriMesh):
        self.mesh = mesh
        self.num_v = len(mesh.vertices)

    def parameterize(self, pinned_indices: Optional[List[int]] = None, pinned_coords: Optional[List[Tuple[float, float]]] = None) -> List[Point2D]:
        """
        Computes UV coordinates using LSCM.
        
        Args:
            pinned_indices: Indices of vertices to fix. If None, two distant boundary vertices are picked.
            pinned_coords: (u, v) coordinates for pinned vertices.
            
        Returns:
            A list of Point2D objects representing UV coordinates.
        """
        if pinned_indices is None:
            # Fix two arbitrary distant vertices to avoid trivial solution
            pinned_indices = [0, self.num_v // 2]
            pinned_coords = [(0.0, 0.0), (1.0, 1.0)]

        # 1. Build the LSCM system matrix A
        # The energy is E = sum Area(t) |grad u - i grad v|^2
        # This leads to a system Mx = 0 where x = [u1, u2, ..., v1, v2, ...]
        
        # We build A such that Ax = 0 represents the Cauchy-Riemann equations
        # across all triangles.
        A = lil_matrix((2 * len(self.mesh.faces), 2 * self.num_v))
        
        for i, face in enumerate(self.mesh.faces):
            v_idx = face.v_indices
            p0, p1, p2 = [self.mesh.vertices[idx] for idx in v_idx]
            
            # Local 2D coordinates for the triangle
            # Place p0 at (0,0), p1 at (d10, 0)
            d10 = math.sqrt((p1.x-p0.x)**2 + (p1.y-p0.y)**2 + (getattr(p1, 'z', 0.0)-getattr(p0, 'z', 0.0))**2)
            d20 = math.sqrt((p2.x-p0.x)**2 + (p2.y-p0.y)**2 + (getattr(p2, 'z', 0.0)-getattr(p0, 'z', 0.0))**2)
            d21 = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2 + (getattr(p2, 'z', 0.0)-getattr(p1, 'z', 0.0))**2)
            
            # Angle at p0
            cos_alpha = (d10**2 + d20**2 - d21**2) / (2 * d10 * d20)
            sin_alpha = math.sqrt(max(0.0, 1.0 - cos_alpha**2))
            
            x0, y0 = 0.0, 0.0
            x1, y1 = d10, 0.0
            x2, y2 = d20 * cos_alpha, d20 * sin_alpha
            
            # Triangle area * 2
            area2 = x1 * y2
            inv_area2 = 1.0 / area2 if area2 > 1e-12 else 0.0
            
            # Geometric weights for C-R equations
            # grad u = (1/area2) * [(y1-y2)u0 + (y2-y0)u1 + (y0-y1)u2, (x2-x1)u0 + (x0-x2)u1 + (x1-x0)u2]
            # Cauchy-Riemann: du/dx = dv/dy and du/dy = -dv/dx
            
            # Coefficients for u
            W_ux = [(y1-y2)*inv_area2, (y2-y0)*inv_area2, (y0-y1)*inv_area2]
            W_uy = [(x2-x1)*inv_area2, (x0-x2)*inv_area2, (x1-x0)*inv_area2]
            
            # eq1: du/dx - dv/dy = 0
            # eq2: du/dy + dv/dx = 0
            for j in range(3):
                # eq1
                A[2*i, v_idx[j]] = W_ux[j]
                A[2*i, self.num_v + v_idx[j]] = -W_uy[j]
                # eq2
                A[2*i+1, v_idx[j]] = W_uy[j]
                A[2*i+1, self.num_v + v_idx[j]] = W_ux[j]

        # 2. Solve the constrained system
        # Separate free and pinned variables
        all_vars = np.arange(2 * self.num_v)
        pinned_vars = np.array(pinned_indices + [idx + self.num_v for idx in pinned_indices])
        free_vars = np.delete(all_vars, pinned_vars)
        
        # Build right hand side from pinned values
        b = np.zeros(2 * len(self.mesh.faces))
        pinned_vals = np.array([p[0] for p in pinned_coords] + [p[1] for p in pinned_coords])
        
        A_csr = A.tocsr()
        b -= A_csr[:, pinned_vars] @ pinned_vals
        
        # Solve A_free * x_free = b
        A_free = A_csr[:, free_vars]
        
        # Use normal equations: (A_free^T * A_free) x = A_free^T * b
        AtA = A_free.T @ A_free
        Atb = A_free.T @ b
        
        x_free = spsolve(AtA, Atb)
        
        # 3. Map back to full UV array
        uv_full = np.zeros(2 * self.num_v)
        uv_full[pinned_vars] = pinned_vals
        uv_full[free_vars] = x_free
        
        u = uv_full[:self.num_v]
        v = uv_full[self.num_v:]
        
        return [Point2D(u[i], v[i]) for i in range(self.num_v)]

import math
