# Diffusion Distance

Diffusion distance is an intrinsic metric on a Riemannian manifold (or its discrete mesh representation) that measures the connectivity of points through a diffusion process.

## Overview

Unlike Euclidean distance, which ignores the underlying shape, or Geodesic distance, which is sensitive to small topological changes (like "short circuits"), diffusion distance is robust to noise and captures the global structure of the shape. It is based on the Heat Kernel $K_t(x, y)$, which represents the probability of a random walker moving from $x$ to $y$ in time $t$.

The diffusion distance $d_t(x, y)$ is defined as:
$$d_t^2(x, y) = \int_M |K_t(x, u) - K_t(y, u)|^2 du$$

## Spectral Representation

In the discrete setting, diffusion distance can be computed efficiently using the eigenvalues $\lambda_i$ and eigenvectors $\phi_i$ of the Laplace-Beltrami operator:
$$d_t^2(x, y) = \sum_{i=1}^k e^{-2\lambda_i t} (\phi_i(x) - \phi_i(y))^2$$

This allows for a **diffusion embedding** where each vertex $x$ is mapped to a point in $\mathbb{R}^k$:
$$\Psi_t(x) = (e^{-\lambda_1 t}\phi_1(x), e^{-\lambda_2 t}\phi_2(x), \dots, e^{-\lambda_k t}\phi_k(x))$$
The Euclidean distance in this embedding space is exactly the diffusion distance.

## Usage

```python
from compgeom.mesh.volume.spectral_geometry import SpectralGeometry

# Compute distance between vertex indices i and j
dist = SpectralGeometry.compute_diffusion_distance(mesh, i, j, t=1.0)

# Compute full embedding
embedding = SpectralGeometry.compute_diffusion_embedding(mesh, t=1.0, k=50)
```

## References
- Coifman, R. R., & Lafon, S. "Diffusion maps." Applied and Computational Harmonic Analysis, 2006.
- Bronstein, A. M., et al. "Numerical Geometry of Non-Rigid Shapes." Springer, 2008.
