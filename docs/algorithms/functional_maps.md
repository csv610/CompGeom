# Functional Maps (Shape Matching)

## 1. Overview
Functional maps are a powerful framework for finding correspondences between 3D shapes. Instead of mapping points directly to points, which is a combinatorial problem, functional maps represent the correspondence as a linear operator between **functions** defined on the surfaces. This transformation from a point-based to a functional representation turns the non-convex matching problem into a much simpler linear algebra problem in a reduced basis.

## 2. Definitions
*   **Basis Functions ($\phi_i$)**: A set of smooth functions defined on a surface, typically the eigenfunctions of the Laplace-Beltrami operator.
*   **Functional Map ($C$)**: A matrix that maps coefficients of a function in shape A's basis to coefficients in shape B's basis.
*   **Correspondance ($\Pi$)**: A mapping from vertices of shape A to vertices of shape B.
*   **Commutativity**: The property that a functional map should commute with other geometric operators (like the Laplacian).

## 3. Theory
Given two shapes $M$ and $N$, we compute the first $k$ eigenfunctions of their respective Laplacians: $\Phi = [\phi_1, \dots, \phi_k]$ and $\Psi = [\psi_1, \dots, \psi_k]$. Any function $f$ on surface $M$ can be approximated as $f \approx \Phi \mathbf{a}$.

A correspondence between $M$ and $N$ can be represented by a matrix $C$ such that if $f$ is a function on $M$ and $g$ is its corresponding function on $N$, then $\mathbf{b} = C \mathbf{a}$, where $\mathbf{b}$ are the coefficients of $g$ in basis $\Psi$.

The matrix $C$ is found by solving an optimization problem:
$$\min_C \| C A - B \|^2 + \alpha \| C \Delta_M - \Delta_N C \|^2$$
where $A$ and $B$ are coefficients of "descriptor functions" (like curvature or HKS) that should be preserved under the mapping.

## 4. Pseudo code
```python
function ComputeFunctionalMap(mesh_A, mesh_B, num_basis=50):
    # 1. Compute Eigenbasis
    L_A, M_A = ComputeLaplacianAndMass(mesh_A)
    L_B, M_B = ComputeLaplacianAndMass(mesh_B)
    evals_A, Phi = scipy.sparse.linalg.eigsh(L_A, M_A, k=num_basis)
    evals_B, Psi = scipy.sparse.linalg.eigsh(L_B, M_B, k=num_basis)
    
    # 2. Compute Descriptors (e.g., Heat Kernel Signatures)
    desc_A = ComputeHKS(mesh_A, Phi, evals_A)
    desc_B = ComputeHKS(mesh_B, Psi, evals_B)
    
    # 3. Project descriptors to basis
    A_coeffs = Phi.T * M_A * desc_A
    B_coeffs = Psi.T * M_B * desc_B
    
    # 4. Solve for Functional Map C (Linear Least Squares)
    # C * A_coeffs = B_coeffs
    C = SolveLeastSquares(A_coeffs.T, B_coeffs.T).T
    
    # 5. Refine C using ICP in functional space (Optional)
    C = RefineMap(C, Phi, Psi)
    
    return C
```

## 5. Parameters Selections
*   **Number of Basis Functions ($k$ )**: Typically 30–100. More basis functions capture more detail but increase computation and noise sensitivity.
*   **Descriptors**: High-quality descriptors (like HKS, WKS, or SHOT) are critical for a good initial map.
*   **Regularization**: Weighting the Laplacian commutativity term helps ensure the map is "smooth" and "geometric."

## 6. Complexity
*   **Eigen-decomposition**: $O(N^{1.5})$ for sparse Laplacian matrices.
*   **Map Calculation**: $O(k^3 + k^2 \cdot D)$ where $D$ is the number of descriptors.
*   **Point Recovery**: $O(N \cdot k)$ using nearest neighbor search in the spectral embedding.

## 7. Usages
*   **Shape Matching**: Finding how one 3D character corresponds to another for animation transfer.
*   **Statistical Shape Analysis**: Building a "mean shape" from a collection of scanned objects.
*   **Texture Transfer**: Mapping a texture from one model to another with a different topology.
*   **Symmetry Detection**: Finding self-correspondences within a single shape.
*   **Shape Interpolation**: Generating intermediate shapes between two models.

## 8. Testing methods and Edge cases
*   **Identical Shapes**: The functional map $C$ should be an identity matrix.
*   **Isometries**: For shapes that are bent but not stretched (like a human in different poses), $C$ should be nearly orthogonal ($C^\top C \approx I$).
*   **Partial Matching**: Test how the algorithm handles shapes where parts are missing (requires more advanced "Partial Functional Maps" logic).
*   **Topology Changes**: Verify that functional maps can still find a reasonable matching even if one shape has a different genus.
*   **Low Resolution**: Ensure the basis is stable even on coarse meshes.

## 9. References
*   Ovsjanikov, M., Ben-Chen, M., Solomon, J., Butscher, A., & Guibas, L. (2012). "Functional maps: a flexible representation of maps between shapes". ACM TOG.
*   Solomon, J., Nguyen, A., Butscher, A., Guibas, L., & Ovsjanikov, M. (2016). "Soft maps between surfaces". Computer Graphics Forum.
*   Ovsjanikov, M., et al. (2017). "Computing and Processing Correspondences with Functional Maps". SIGGRAPH Course.
*   Wikipedia: [Spectral shape analysis](https://en.wikipedia.org/wiki/Spectral_shape_analysis)
