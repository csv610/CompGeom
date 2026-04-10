# Stochastic PDE Solvers (Walk on Spheres & Stars)

Stochastic PDE solvers use Monte Carlo methods to solve partial differential equations (like Laplace or Poisson) on geometric domains.

## Overview

Unlike standard grid-based solvers (Finite Element/Difference), which require a high-quality global mesh, stochastic solvers like **Walk on Spheres (WoS)** and **Walk on Stars (WoSt)** can solve for the value at a single point without constructing a global system of equations. This is particularly useful for complex or dirty geometries.

## Implementation Details

The `CompGeom` implementation includes:
1.  **Walk on Spheres (WoS)**:
    *   **Laplace Solver**: Estimates $u(x)$ where $\Delta u = 0$.
    *   **Poisson Solver**: Estimates $u(x)$ where $\Delta u = f$.
2.  **Walk on Stars (WoSt)**:
    *   **Gradient Estimator**: Robustly estimates $\nabla u(x)$ using the Boundary Integral Equation (BIE).

## Usage

```python
from compgeom.mesh.algorithms.stochastic_pde import WalkOnSpheres, WalkOnStars
from compgeom import Point3D

# Initialize on a surface mesh
wos = WalkOnSpheres(mesh)
value = wos.solve_laplace(Point3D(0.5, 0.5, 0.5), boundary_func)

# Robust gradient estimation
wost = WalkOnStars(mesh)
grad = wost.solve_gradient(Point3D(0.5, 0.5, 0.5), boundary_func)
```

## References
- Sawhney, R., & Crane, K. "Monte Carlo Geometry Processing: A Meshless Approach to Geometric PDE." ACM Transactions on Graphics (SIGGRAPH), 2020.
- Yu, Y., et al. "Robust Derivative Estimation with Walk on Stars." ACM Transactions on Graphics (SIGGRAPH), 2025.
