# Wave Kernel Signature (WKS)

## 1. Overview
The Wave Kernel Signature (WKS) is a multi-scale geometric descriptor for vertices on a 3D mesh. Like the Heat Kernel Signature (HKS), it is based on the spectral properties of the Laplace-Beltrami operator. However, while HKS models heat diffusion (essentially a low-pass filter), WKS models the evolution of a quantum particle (wave function) with a specific energy distribution. This makes WKS better at capturing high-frequency geometric details and provides superior performance in non-rigid shape matching.

## 2. Definitions
*   **Schrödinger Equation**: The PDE describing the evolution of a quantum state: $i \frac{\partial \psi}{\partial t} = \Delta \psi$.
*   **Energy Level ($E$ )**: A specific frequency or eigenvalue of the Laplacian.
*   **Energy Distribution ($g_E$ )**: A band-pass filter (typically Gaussian) centered at energy $E$ used to weight the Laplacian eigenvalues.
*   **Multi-scale Descriptor**: A vector associated with each vertex where each entry corresponds to a different energy level.

## 3. Theory
The Wave Kernel Signature $W(x, e)$ at vertex $x$ and energy scale $e$ is defined as the average probability of a particle with energy distribution $g_e$ being found at $x$:
$$W(x, e) = \sum_{k=1}^\infty g_e(\lambda_k)^2 \phi_k(x)^2$$
where $\lambda_k$ and $\phi_k$ are the eigenvalues and eigenfunctions of the Laplace-Beltrami operator.

The filter $g_e$ is usually a log-normal distribution:
$$g_e(\lambda) = \exp \left( -\frac{(\log e - \log \lambda)^2}{2\sigma^2} \right)$$
This ensures that the descriptor is sensitive to relative energy differences, providing a balanced representation of both coarse and fine geometric features.

## 4. Pseudo code
```python
function ComputeWKS(mesh, num_basis=100, num_scales=100):
    # 1. Compute Eigenbasis
    L, M = BuildDiscreteLaplacian(mesh)
    evals, Phis = scipy.sparse.linalg.eigsh(L, M, k=num_basis, sigma=-1e-6)
    
    # 2. Define Energy Scales (log-space)
    e_min = log(evals[1]) # Skip zero eigenvalue
    e_max = log(evals[-1])
    scales = np.linspace(e_min, e_max, num_scales)
    sigma = (e_max - e_min) / num_scales * 7.0 # Heuristic width
    
    # 3. Compute Descriptor for each vertex
    wks = np.zeros((num_vertices, num_scales))
    for i, e in enumerate(scales):
        # Apply band-pass filter to eigenvalues
        weights = exp(-(e - log(evals))**2 / (2 * sigma**2))
        
        # Normalize weights to sum to 1 (optional)
        weights /= sum(weights)
        
        # Accumulate weighted squared eigenfunctions
        # wks[:, i] = sum_k (weights[k] * Phis[:, k]^2)
        wks[:, i] = (Phis**2) @ weights
        
    return wks
```

## 5. Parameters Selections
*   **Number of Eigenfunctions ($k$ )**: Typically 100–300. More eigenfunctions are needed than for HKS to capture the "wave" behavior.
*   **Filter Width ($\sigma$ )**: Controls the trade-off between spatial and spectral localization.
*   **Scale Range**: Usually spans the entire computed spectrum in log-space.

## 6. Complexity
*   **Eigen-decomposition**: $O(N^{1.5})$ for sparse matrices.
*   **Signature Calculation**: $O(N \cdot k \cdot S)$ where $S$ is the number of scales.
*   **Space Complexity**: $O(N \cdot S)$ to store the descriptors.

## 7. Usages
*   **Non-Rigid Shape Matching**: Finding corresponding points between different poses of the same object (e.g., a human walking).
*   **Shape Retrieval**: Creating a global descriptor by pooling WKS values across the mesh.
*   **Symmetry Detection**: Identifying vertices with similar geometric contexts.
*   **Segment Classification**: Training machine learning models to identify parts of a mesh (e.g., "head," "arm," "leg").

## 8. Testing methods and Edge cases
*   **Isometry Invariance**: Verify that WKS is identical for a mesh in two different isometric poses.
*   **Scale Invariance**: WKS is NOT naturally scale-invariant (unlike HKS with normalization). Test how it behaves when the mesh is scaled.
*   **Locality**: Verify that WKS correctly identifies high-curvature regions (like fingertips or nose) as having distinct signatures.
*   **Low Resolution**: Ensure the signature remains stable even on coarse triangulations.
*   **Spectral Truncation**: Observe how the descriptor quality degrades as the number of basis functions $k$ is reduced.

## 9. References
*   Aubry, M., Schlickewei, U., & Cremers, D. (2011). "The wave kernel signature: A quantum mechanical approach to shape analysis". ICCV Workshops.
*   Sun, J., Ovsjanikov, M., & Guibas, L. (2009). "A concise and provably informative multi-scale signature based on heat diffusion". Computer Graphics Forum. (Context for HKS vs WKS).
*   Bronstein, M. M., & Kokkinos, I. (2010). "Scale-invariant heat kernel signatures for non-rigid shape retrieval". CVPR.
*   Wikipedia: [Spectral shape analysis](https://en.wikipedia.org/wiki/Spectral_shape_analysis)
