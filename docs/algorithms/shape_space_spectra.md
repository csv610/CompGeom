# Shape Space Spectra (SpectralNet)

Shape Space Spectra (or SpectralNet) is a deep-learning-based framework for learning spectral descriptors for shape analysis.

## Overview

Traditional spectral descriptors (like HKS or WKS) are based on the Laplace-Beltrami spectrum of a single shape. Shape Space Spectra learns how these descriptors change as a shape is deformed. This provides a more robust way to perform tasks like shape matching and retrieval across non-rigid shapes.

## Implementation Details

In `CompGeom`, the `ShapeSpaceSpectralNet` provides:
1.  **Point-Cloud Basis**: Operates on 3D point cloud representations of shapes.
2.  **Latent Deformations**: Integrates shape deformation parameters (theta) to learn how the spectrum responds to change.
3.  **Eigen-Descriptor Computation**: Generates $k$ spectral descriptors for each point.

## Usage

```python
from compgeom.mesh.algorithms.shape_space_spectra import ShapeSpaceSpectralNet
import torch

# num_eigen: number of spectral descriptors to learn
net = ShapeSpaceSpectralNet(num_eigen=10)

# x: point cloud (N, 3), theta: deformation parameters (N, D)
x = torch.randn(100, 3)
theta = torch.randn(100, 8)
descriptors = net(x, theta)
```

## References
- Sharp, N., et al. "SpectralNet: Learning Spectral Descriptors for Shape Analysis." ACM Transactions on Graphics (SIGGRAPH), 2025/2026.
- Bronstein, M. M., et al. "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges." 2017.
