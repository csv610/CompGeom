# Hodge Decomposition (Vector Field Decomposition)

## 1. Overview
The Hodge-Helmholtz Decomposition (often simply Hodge Decomposition) is a fundamental theorem in vector calculus and differential geometry that states any vector field can be uniquely decomposed into three orthogonal components: a curl-free component (the gradient of a scalar potential), a divergence-free component (the curl of a vector potential), and a harmonic component (representing flow around topological "holes"). In the context of 2D surface meshes, it provides a powerful way to analyze and manipulate tangent vector fields.

## 2. Definitions
*   **Exact Component ($\omega_{exact}$)**: The gradient of a scalar function $\alpha$, $\omega_{exact} = d\alpha$. These are **curl-free**.
*   **Co-exact Component ($\omega_{co-exact}$)**: The "rotational" part, represented as $\omega_{co-exact} = \star d\beta$. These are **divergence-free**.
*   **Harmonic Component ($\omega_{harmonic}$)**: A field that is both curl-free and divergence-free, $d\omega = \delta\omega = 0$. These depend on the topology of the mesh.
*   **Helmholtz-Hodge Theorem**: For any 1-form $\omega$: $\omega = d\alpha + \delta\beta + \gamma$, where $d\alpha$ is exact, $\delta\beta$ is co-exact, and $\gamma$ is harmonic.

## 3. Theory
In Discrete Exterior Calculus (DEC), the decomposition is performed by solving two separate Poisson equations:
1.  **Gradient Part**: Minimize the energy $\| \omega - d\alpha \|^2$ to find the scalar potential $\alpha$. This leads to the linear system $\Delta \alpha = \delta \omega$, where $\delta = \star^{-1} d^\top \star$ is the codifferential (divergence).
2.  **Curl Part**: Minimize the energy $\| \omega - \delta\beta \|^2$ to find the dual potential $\beta$. This leads to the linear system $\Delta \beta = d \omega$, where $d$ is the curl.
3.  **Harmonic Part**: The remainder $\gamma = \omega - d\alpha - \delta\beta$ is the harmonic component.

Orthogonality between these components is guaranteed by the $d \circ d = 0$ property and the definition of the Hodge star.

## 4. Pseudo code
```python
function HodgeDecompose(omega, mesh):
    # 1. Compute discrete operators
    d0, d1 = ComputeExteriorDerivatives(mesh)
    star0, star1, star2 = ComputeHodgeStars(mesh)
    
    # 2. Find Exact Component (d*alpha)
    # Solve (d0.T * star1 * d0) * alpha = (d0.T * star1 * omega)
    Laplacian_0 = d0.T * star1 * d0
    rhs_exact = d0.T * star1 * omega
    alpha = SolveSparse(Laplacian_0, rhs_exact)
    exact_part = d0 * alpha
    
    # 3. Find Co-exact Component (*d*beta)
    # Solve (d1 * star1.inv * d1.T) * beta_hat = (d1 * star1.inv * star1 * omega)
    # Using dual 0-forms for beta_hat
    Laplacian_1 = d1 * star1.inv * d1.T
    rhs_coexact = d1 * omega
    beta_hat = SolveSparse(Laplacian_1, rhs_coexact)
    coexact_part = star1.inv * d1.T * star2.inv * beta_hat
    
    # 4. Harmonic Part
    harmonic_part = omega - exact_part - coexact_part
    
    return exact_part, coexact_part, harmonic_part
```

## 5. Parameters Selections
*   **Boundary Conditions**: For meshes with boundaries, the decomposition is not unique unless boundary conditions are specified (e.g., $d\alpha$ is normal or tangent to the boundary).
*   **Sparse Solver**: Cholesky factorization (via `scipy.sparse.linalg.factorized`) is recommended as the Laplacian matrices are symmetric and positive semi-definite.

## 6. Complexity
*   **Time Complexity**: $O(E^{1.5})$ where $E$ is the number of edges, dominated by the sparse linear solver performance.
*   **Space Complexity**: $O(E)$ to store the discrete operators and the field vectors.

## 7. Usages
*   **Vector Field Design**: Creating smooth vector fields for hair, fur, or pen-and-ink rendering by manipulating the potentials.
*   **Surface Parameterization**: Constructing "conformal" maps by ensuring the gradient field of UV coordinates is harmonic.
*   **Fluid Animation**: Extracting the rotational (co-exact) part of a flow for vortex visualization or removing divergence to maintain volume.
*   **Shape Matching**: Using harmonic components as topological signatures for 3D models.
*   **Meteorology**: Analyzing global wind patterns into geostrophic (exact) and ageostrophic components.

## 8. Testing methods and Edge cases
*   **Pure Gradient Field**: If $\omega = d\phi$ for some random scalar $\phi$, then the co-exact and harmonic parts should be nearly zero.
*   **Zero-Genus Mesh**: On a mesh with the topology of a sphere (genus 0), the harmonic part should be exactly zero.
*   **Topological Holes**: On a torus (genus 1), a non-zero harmonic component should appear as a field that "wraps" around the hole without having any divergence or curl.
*   **Exactness Verification**: Verify that $d_1 \times \text{exact\_part} \approx 0$ and $\delta \times \text{coexact\_part} \approx 0$.

## 9. References
*   Polthier, K., & Preuss, E. (2003). "Identifying vector field singularities using a discrete Hodge decomposition". Visualization and Mathematics III.
*   Tong, Y., Lombeyda, S., Hirani, A. N., & Desbrun, M. (2003). "Discrete Multiscale Vector Field Decomposition". ACM TOG.
*   Crane, K. (2013). "Digital Geometry Processing with Discrete Exterior Calculus". SIGGRAPH Course.
*   Wikipedia: [Helmholtz decomposition](https://en.wikipedia.org/wiki/Helmholtz_decomposition)
