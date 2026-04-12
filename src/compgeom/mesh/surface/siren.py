"""
SIREN (Implicit Neural Representations with Periodic Activations) for geometry.
Sitzmann et al., "Implicit Neural Representations with Periodic Activation Functions", NeurIPS 2020.
Used widely in SIGGRAPH geometry research (2020-2025).
"""

import torch
import torch.nn as nn

import numpy as np
from typing import List, Tuple, Optional


class SineLayer(nn.Module):
    """Linear layer with sine activation and specialized SIREN initialization."""
    def __init__(self, in_features, out_features, bias=True, is_first=False, omega_0=30):
        super().__init__()
        self.omega_0 = omega_0
        self.is_first = is_first
        self.in_features = in_features
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        self.init_weights()

    def init_weights(self):
        with torch.no_grad():
            if self.is_first:
                self.linear.weight.uniform_(-1 / self.in_features, 1 / self.in_features)
            else:
                self.linear.weight.uniform_(-np.sqrt(6 / self.in_features) / self.omega_0, 
                                             np.sqrt(6 / self.in_features) / self.omega_0)

    def forward(self, input):
        return torch.sin(self.omega_0 * self.linear(input))

class SIREN(nn.Module if nn else object):
    """
    SIREN model for representing SDFs or other geometric fields.
    Excellent at capturing sharp details and gradients (normals).
    """
    def __init__(self, in_features=3, out_features=1, hidden_features=256, hidden_layers=3, outermost_linear=True):
        if nn is None:
            raise ImportError("SIREN requires 'torch'. Please install it to use this module.")
        super().__init__()
        self.net = []
        # First layer
        self.net.append(SineLayer(in_features, hidden_features, is_first=True))
        # Hidden layers
        for _ in range(hidden_layers):
            self.net.append(SineLayer(hidden_features, hidden_features, is_first=False))
        # Output layer
        if outermost_linear:
            self.net.append(nn.Linear(hidden_features, out_features))
        else:
            self.net.append(SineLayer(hidden_features, out_features, is_first=False))
        self.net = nn.Sequential(*self.net)

    def forward(self, coords):
        """Forward pass: (N, 3) -> (N, out_features)."""
        return self.net(coords)

    def get_gradient(self, coords):
        """Analytic gradient (normals) using autograd."""
        coords = coords.clone().detach().requires_grad_(True)
        output = self.forward(coords)
        grad = torch.autograd.grad(output, coords, 
                                  grad_outputs=torch.ones_like(output), 
                                  create_graph=True)[0]
        return grad
