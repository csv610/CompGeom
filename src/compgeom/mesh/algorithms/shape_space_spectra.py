"""
Shape Space Spectra (SIGGRAPH 2025 Best Paper).
Differentiable eigenanalysis for continuously parameterized shape families.
Chang et al., "Shape Space Spectra", 2025.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional, Callable

try:
    import torch
    import torch.nn as nn
except ImportError:
    torch = None
    nn = None

class ShapeSpaceSpectralNet(nn.Module if nn else object):
    """
    Learns eigenfunctions as a neural field phi(x; theta) across a shape space.
    The network takes (spatial coordinates x, shape parameters theta).
    """
    def __init__(self, x_dim: int = 3, theta_dim: int = 8, num_eigen: int = 10, hidden_dim: int = 128):
        if nn is None:
            raise ImportError("ShapeSpaceSpectralNet requires 'torch'.")
        super().__init__()
        self.num_eigen = num_eigen
        
        # Shared backbone for processing (x, theta)
        self.backbone = nn.Sequential(
            nn.Linear(x_dim + theta_dim, hidden_dim),
            nn.Softplus(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Softplus(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Softplus(),
            nn.Linear(hidden_dim, num_eigen) # Output all k eigenfunctions
        )

    def forward(self, x: torch.Tensor, theta: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (N, 3) points.
            theta: (N, d_theta) shape parameters.
        Returns:
            (N, k) eigenfunction values.
        """
        feat = torch.cat([x, theta], dim=-1)
        return self.backbone(feat)

    def compute_loss(self, x: torch.Tensor, theta: torch.Tensor, is_inside: torch.Tensor):
        """
        Variational loss based on Dirichlet energy and orthogonality.
        is_inside: (N, 1) boolean mask defining the domain for theta.
        """
        # 1. Gradient computation
        x.requires_grad_(True)
        phi = self.forward(x, theta)
        
        # Dirichlet Energy: sum_k integral ||grad phi_k||^2
        # Use only points inside the domain
        phi_in = phi * is_inside
        
        dirichlet_loss = 0.0
        for k in range(self.num_eigen):
            grad_phi_k = torch.autograd.grad(phi_in[:, k].sum(), x, create_graph=True)[0]
            dirichlet_loss += torch.mean(torch.sum(grad_phi_k**2, dim=-1))
            
        # 2. Orthogonality and Unit Norm constraints
        # Gram matrix: G_ij = integral(phi_i * phi_j)
        # Should be Identity matrix
        phi_flat = phi[is_inside.squeeze() > 0.5]
        if phi_flat.shape[0] > 0:
            gram = (phi_flat.T @ phi_flat) / phi_flat.shape[0]
            constraint_loss = torch.norm(gram - torch.eye(self.num_eigen, device=phi.device))**2
        else:
            constraint_loss = 0.0
            
        return dirichlet_loss + 10.0 * constraint_loss

    def get_eigenvalues(self, x: torch.Tensor, theta: torch.Tensor, is_inside: torch.Tensor) -> torch.Tensor:
        """
        Estimates eigenvalues using the Rayleigh quotient:
        lambda_k = integral ||grad phi_k||^2 / integral phi_k^2
        """
        x.requires_grad_(True)
        phi = self.forward(x, theta)
        phi_in = phi * is_inside
        
        evals = []
        for k in range(self.num_eigen):
            grad_phi_k = torch.autograd.grad(phi_in[:, k].sum(), x, create_graph=True)[0]
            numerator = torch.mean(torch.sum(grad_phi_k**2, dim=-1))
            denominator = torch.mean(phi_in[:, k]**2)
            evals.append(numerator / (denominator + 1e-12))
            
        return torch.stack(evals)
