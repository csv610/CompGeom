# BFF Parameterization (Boundary First Flattening)

## 1. Overview
Boundary First Flattening (BFF) is a state-of-the-art method for **conformal parameterization** of surface meshes, introduced by Keenan Crane et al. in 2017. Unlike traditional methods like Harmonic Mapping or LSCM, BFF allows the user to prescribe the target boundary curvature, providing unmatched control over the flattening process (e.g., flattening to a disk, a rectangle, or a specific shape).

## 2. Definitions
*   **Conformal Mapping:** A mapping that locally preserves angles.
*   **Laplacian Matrix ($L$):** A discrete representation of the Laplace-Beltrami operator, typically constructed using cotangent weights.
*   **Scale Factor ($u$):** A scalar field on the mesh representing the local scaling needed to achieve the target metric.
*   **Geodesic Curvature ($\kappa$):** The curvature of a curve on a surface, relative to the surface itself.

## 3. Theory
BFF is rooted in the **Yamabe equation**, which describes how the metric changes under a conformal transformation $g' = e^{2u}g$. The target geodesic curvature $\kappa'$ on the boundary relates to the original curvature $\kappa$ and the normal derivative of the scale factor $u$ by:
$$\kappa' = e^{-u}(\kappa + \frac{\partial u}{\partial n})$$
BFF solves this by:
1. Determining boundary scale factors $u$ that satisfy the target curvature $\kappa'$.
2. Extending $u$ to the interior via a Dirichlet problem.
3. Integrating the flattened boundary and extending the UV coordinates harmonically to the interior.

## 4. Pseudo code
```python
Algorithm: BFF Parameterization
Input: Triangular mesh M
Output: 2D coordinates (UV) for each vertex

1. Build the cotangent Laplacian matrix L for mesh M.
2. Identify the boundary loop of M.
3. Compute the current geodesic curvature kappa at each boundary vertex.
4. Define the target curvature kappa_target (e.g., 2*pi/n for disk).
5. Solve the boundary system for scale factors u_b:
   L_bb * u_b = kappa_target - kappa
6. Solve the Dirichlet problem for interior scale factors u_i:
   L_ii * u_i = -L_ib * u_b
7. Integrate boundary coordinates uv_b using l_flat = l_orig * exp((u_i + u_j)/2).
8. Extend uv_b to the interior via harmonic mapping:
   L_ii * uv_i = -L_ib * uv_b
```

## 5. Parameters Selections
*   **Target Curvature:** For a disk, set to $2\pi/n$. For a rectangle, set to $\pi/2$ at four vertices and $0$ elsewhere.
*   **Solver:** Sparse direct solvers (like SuperLU) are recommended for solving the Laplacian systems.

## 6. Complexity
*   **Construction:** $O(N)$ for building the Laplacian.
*   **Solving:** $O(N^{1.5})$ to $O(N^2)$ depending on mesh connectivity and sparse solver performance.

## 7. Usages
Implemented in `compgeom.mesh.surface.parameterization_bff.BFFParameterizer`. Used for UV unwrapping, texture mapping, and surface remeshing.

## 8. Testing methods and Edge cases
*   **Testing:** Verify local angle preservation (conformal property). Check boundary curvature error.
*   **Edge Cases:** Non-manifold meshes, meshes with no boundary (unsupported), and self-intersecting UV outputs.

## 9. References
*   Crane, K., Weischedel, C., & Wardetzky, M. (2017). "Boundary first flattening". ACM TOG.
*   Wikipedia: [Conformal mapping](https://en.wikipedia.org/wiki/Conformal_mapping)
