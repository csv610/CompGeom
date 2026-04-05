# Shape Space Spectra (Laplacian Eigenvalues)

## 1. Overview
The spectrum of a shape refers to the set of eigenvalues of its Laplace-Beltrami operator. In geometric modeling, these eigenvalues (and their corresponding eigenfunctions) act as a "geometric DNA" or "fingerprint" that describes the intrinsic shape of a manifold. Shape space spectra are used for shape matching, classification, and analysis because they are invariant under isometric transformations (bending without stretching). The field is often summarized by the question posed by Mark Kac: "Can one hear the shape of a drum?"

## 2. Definitions
*   **Laplace-Beltrami Operator ($\Delta$)**: The generalization of the Laplacian to manifolds.
*   **Spectrum**: The sequence of eigenvalues $0 = \lambda_0 \le \lambda_1 \le \lambda_2 \le \dots$.
*   **Eigenfunction ($\phi$)**: A non-zero function such that $\Delta \phi = \lambda \phi$.
*   **Heat Kernel**: A function that describes how heat diffuses over the surface, which can be expressed in terms of the spectrum.
*   **Shape-DNA**: A descriptor formed by the first $k$ eigenvalues of the Laplacian.

## 3. Theory
The Laplacian spectrum encodes information about the area, perimeter, and topology of a shape. 
1.  **Weyl's Law**: The growth rate of eigenvalues relates to the volume (area) of the shape: $\lambda_n \sim \frac{4\pi n}{Area}$.
2.  **Isometry Invariance**: Two isometric shapes have identical spectra. However, the converse is not always true (there exist non-isometric "isospectral" shapes).
3.  **Fundamental Tone**: $\lambda_1$ (the Fiedler value) relates to the "width" or "length" of the shape and is used for spectral clustering and graph partitioning.

The spectrum is computed by discretizing the Laplacian on a mesh using **cotangent weights** and solving a generalized eigenvalue problem: $L \Phi = \Lambda M \Phi$, where $L$ is the stiffness matrix and $M$ is the mass matrix.

## 4. Pseudo code
```python
function ComputeShapeDNA(mesh, k):
    # 1. Build discrete Laplacian and Mass matrices
    # L is the cotangent stiffness matrix
    # M is the diagonal lumped mass matrix (vertex areas)
    L, M = BuildDiscreteLaplacian(mesh)
    
    # 2. Solve generalized eigenvalue problem
    # Find the k smallest eigenvalues
    # Shift-invert mode is used for efficiency
    eigenvalues, eigenfunctions = scipy.sparse.linalg.eigsh(L, M, k=k, sigma=-1e-6)
    
    # 3. Normalize spectrum
    # Often normalized by the surface area to achieve scale invariance
    area = mesh.CalculateTotalArea()
    normalized_dna = eigenvalues * area
    
    return normalized_dna, eigenfunctions
```

## 5. Parameters Selections
*   **Number of Eigenvalues ($k$ )**: Typically 10–100. More eigenvalues provide more detail but are more sensitive to mesh noise.
*   **Normalization**: Normalizing by $\lambda_1$ or the total area is necessary to compare shapes of different sizes.
*   **Lumped vs. Consistent Mass**: Using a diagonal lumped mass matrix is faster and usually sufficient for shape analysis.

## 6. Complexity
*   **Matrix Construction**: $O(F)$ where $F$ is the face count.
*   **Eigen-decomposition**: $O(N^{1.5})$ for sparse matrices using Lanczos or LOBPCG methods.
*   **Space Complexity**: $O(N \cdot k)$ to store the eigenfunctions.

## 7. Usages
*   **Shape Retrieval**: Searching a 3D database for models that "look like" a query object.
*   **Symmetry Detection**: Identifying self-isometries of a shape.
*   **Mesh Segmentation**: Partitioning a mesh into functional parts based on the nodal sets of eigenfunctions.
*   **Graph Partitioning**: Using the second eigenvector (Fiedler vector) to split a mesh into two balanced pieces.
*   **Style Analysis**: Classifying models into categories (e.g., "human," "animal," "chair") based on their spectral signatures.

## 8. Testing methods and Edge cases
*   **Simple Geometries**: Verify that the spectrum of a sphere or a cube matches known analytical or high-precision values.
*   **Area Invariance**: Ensure that scaling a mesh and then normalizing the spectrum yields the same DNA.
*   **Mesh Refinement**: Verify that the eigenvalues converge as the mesh resolution increases.
*   **Disconnected Components**: The number of zero eigenvalues ($\lambda=0$) should match the number of connected components.
*   **Isospectral Shapes**: Test on known pairs of isospectral shapes (like the "drums" of Gordon, Webb, and Wolpert) to see if they can be distinguished by other means.

## 9. References
*   Kac, M. (1966). "Can one hear the shape of a drum?". American Mathematical Monthly.
*   Reuter, M., Wolter, F. E., & Peinecke, N. (2006). "Laplace–Beltrami spectra as 'Shape-DNA' of surfaces and solids". Computer-Aided Design.
*   Levy, B. (2006). "Laplace-Beltrami Eigenfunctions towards an Optimal Tool for Geology and Geometry". SMA.
*   Wikipedia: [Spectral shape analysis](https://en.wikipedia.org/wiki/Spectral_shape_analysis)
