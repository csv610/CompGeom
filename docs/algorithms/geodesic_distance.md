# Shortest Path on Meshes (Geodesic Distance)

## 1. Overview
Finding the shortest path between two points on a 3D surface mesh (the geodesic distance) is a fundamental problem in geometric modeling. Unlike Euclidean distance, which ignores the surface, the geodesic distance must follow the "terrain" of the mesh. While the Fast Marching Method (FMM) is the most famous numerical approach, other algorithms like the MMP algorithm (exact) and the Heat Method (highly efficient) provide different trade-offs between speed and accuracy.

## 2. Definitions
*   **Geodesic**: The shortest path between two points on a surface, restricted to stay on that surface.
*   **MMP Algorithm**: An exact algorithm that generalizes Dijkstra's to continuous surfaces by propagating "windows" along edges.
*   **Heat Method**: A modern method that approximates geodesics by observing the flow of heat from a source point.
*   **Edge-Walking**: A simple approximation that treats the mesh as a graph and uses Dijkstra's algorithm on edges (usually provides poor results as it can't "cut" across faces).

## 3. Theory
### MMP Algorithm (Exact)
The MMP algorithm (Mitchell, Mount, and Papadimitriou) works by propagating "intervals" of potential paths across the surface. When a wavefront reaches an edge, it creates a new set of intervals for the next triangle. This results in an exact polyhedral geodesic but is mathematically complex to implement.

### The Heat Method (Fast Approximation)
The Heat Method, introduced by Keenan Crane et al. (2013), uses a three-step process based on the heat equation:
1.  **Heat Flow**: Solve the heat equation $\dot{u} = \Delta u$ for a short time $t$, with a source at the starting vertex.
2.  **Gradient Normalization**: Calculate the gradient of the heat field $\nabla u$ and normalize it to have unit length ($X = -\nabla u / |\nabla u|$).
3.  **Poisson Solve**: Solve the Poisson equation $\Delta \phi = \nabla \cdot X$. The resulting scalar field $\phi$ is the geodesic distance to the source.

## 4. Pseudo code
### Heat Method
```python
function ComputeGeodesicHeat(mesh, source_vertex):
    # 1. Build discrete operators
    L = ComputeCotangentLaplacian(mesh)
    A = ComputeVertexAreas(mesh)
    
    # 2. Integrate heat flow (Backward Euler)
    # Solve (A - t*L) * u = delta_source
    t = mean_edge_length(mesh)**2
    u = SolveLinearSystem(A - t*L, source_indicator)
    
    # 3. Calculate and normalize gradients
    X = []
    for face in mesh.faces:
        grad_u = ComputeFaceGradient(face, u)
        X.append(-grad_u / norm(grad_u))
        
    # 4. Solve Poisson equation
    # Solve L * phi = divergence(X)
    div_X = ComputeDivergence(X, mesh)
    phi = SolveLinearSystem(L, div_X)
    
    # Shift so source is 0
    return phi - phi[source_vertex]
```

## 5. Parameters Selections
*   **Time Step ($t$ )**: In the Heat Method, $t$ is typically set to the square of the average edge length. Too small $t$ leads to numerical noise; too large $t$ leads to smoothing errors.
*   **Solver**: Sparse direct solvers (like SuperLU or CHOLMOD) are essential for the Laplacian systems.

## 6. Complexity
*   **MMP Algorithm**: $O(n^2)$ in the worst case, but $O(n \log n)$ in practice.
*   **Heat Method**: $O(n)$ after an initial $O(n^{1.5})$ matrix factorization. Subsequent queries from different sources are extremely fast.

## 7. Usages
*   **Surface Parameterization**: Normalizing distances for texture mapping.
*   **Mesh Segmentation**: Grouping vertices based on their distance from a set of "seeds."
*   **Shape Matching**: Using geodesic "fingerprints" to compare 3D models.
*   **Texture Synthesis**: Propagation of patterns along a surface.
*   **Medicine**: Measuring distances along the folds of the brain or surface of an organ.

## 8. Testing methods and Edge cases
*   **Flat Mesh**: The results should match the Euclidean distance exactly.
*   **Sphere**: Geodesics between any two points should follow "Great Circles."
*   **Concave Regions**: Verify that the path correctly "bends" into valleys rather than jumping across them.
*   **Mesh Resolution**: Test how the accuracy of the Heat Method improves as the mesh is refined.
*   **Boundaries**: Ensure the algorithm handles the edges of a surface without "leaking" or crashing.

## 9. References
*   Mitchell, J. S. B., Mount, D. M., & Papadimitriou, C. H. (1987). "The discrete geodesic problem". SIAM Journal on Computing.
*   Crane, K., Weischedel, C., & Wardetzky, M. (2013). "Geodesics in Heat: A New Approach to Computing Distance Based on Heat Flow". ACM TOG.
*   Surazhsky, V., Surazhsky, O., Kirsanov, D., Gortler, S. J., & Hoppe, H. (2005). "Fast exact and approximate geodesics on meshes". SIGGRAPH.
*   Wikipedia: [Geodesic](https://en.wikipedia.org/wiki/Geodesic)
