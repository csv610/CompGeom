"""
1-Lipschitz Neural Distance Fields (SGP 2024) for valid SDFs.
Coiffier and Bethune, "1-Lipschitz Neural Distance Fields", 2024.
"""

import torch
import torch.nn as nn
import torch.nn.utils.parametrizations as parametrizations

import numpy as np
from typing import List, Tuple, Optional


class LipschitzSDF(nn.Module):
    """
    Neural network constrained to be 1-Lipschitz.
    This ensures that the output is a valid distance field.
    """
    def __init__(self, in_features: int = 3, hidden_features: int = 128, layers: int = 4):
        if nn is None:
            raise ImportError("LipschitzSDF requires 'torch'.")
        super().__init__()
        
        self.net = []
        curr_in = in_features
        for _ in range(layers):
            # Spectral normalization ensures 1-Lipschitz per layer
            linear = nn.Linear(curr_in, hidden_features)
            self.net.append(parametrizations.spectral_norm(linear))
            # ReLU is 1-Lipschitz
            self.net.append(nn.ReLU())
            curr_in = hidden_features
            
        # Final layer to output distance
        final_linear = nn.Linear(curr_in, 1)
        self.net.append(parametrizations.spectral_norm(final_linear))
        self.net = nn.Sequential(*self.net)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def compute_loss(self, points: torch.Tensor, target_distances: torch.Tensor) -> torch.Tensor:
        """Standard L2 loss. The 1-Lipschitz constraint is handled by architecture."""
        pred = self.forward(points)
        return torch.mean((pred - target_distances)**2)
