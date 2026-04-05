# Mesh Topology Transfer (Harmonic Mapping)

## 1. Overview
Mesh Topology Transfer is the process of adapting a source mesh's connectivity (its faces and edges) to a new geometric boundary. This is achieved using Harmonic Mapping, a technique that positions interior vertices to minimize a "stretching" energy (Dirichlet energy). The result is a new mesh that shares the same topology as the source but fits the geometry of the target domain with minimal distortion.

## 2. Definitions
*   **Topology**: The connectivity of the mesh (which vertices form which faces), independent of their spatial coordinates.
*   **Harmonic Map**: A mapping between geometric domains that satisfies the Laplace equation $\Delta f = 0$.
*   **Barycentric Mapping**: A discrete version of harmonic mapping where every interior vertex is the weighted average of its neighbors.
*   **Dirichlet Energy**: A measure of how much a mapping "stretches" the domain; harmonic maps are the minimizers of this energy.

## 3. Theory
Based on Tutte's Embedding Theorem (1963), a valid planar embedding of a graph can be found by fixing its boundary to a convex polygon and solving for the interior positions such that each vertex is at the centroid of its neighbors. 

Mathematically, for each interior vertex $i$, we solve:
$$V_i = \frac{1}{\sum_{j \in N(i)} w_{ij}} \sum_{j \in N(i)} w_{ij} V_j$$
Where $w_{ij}$ are weights (often $w_{ij} = 1$ for simple barycentric mapping or cotangent weights for more accurate harmonic maps). This forms a system of linear equations $L V = B$, where $L$ is the Laplacian matrix and $B$ contains boundary constraints.

## 4. Pseudo code
```python
function TransferTopology(source_mesh, target_boundary):
    # 1. Identify and parameterize boundaries
    source_boundary = GetBoundaryCycle(source_mesh)
    MapBoundary(source_boundary, target_boundary) # Using arc-length
    
    # 2. Initialize interior vertices
    target_centroid = Centroid(target_boundary)
    for v in InteriorVertices(source_mesh):
        v.position = target_centroid
        
    # 3. Solve Laplace Equation (Iterative Gauss-Seidel)
    for iteration in range(max_iterations):
        max_delta = 0
        for v in InteriorVertices(source_mesh):
            old_pos = v.position
            # Move vertex to the average of its neighbors
            neighbors = GetNeighbors(v, source_mesh)
            v.position = sum(n.position for n in neighbors) / len(neighbors)
            max_delta = max(max_delta, dist(old_pos, v.position))
            
        if max_delta < epsilon: break
        
    return CreateMesh(new_positions, source_mesh.faces)
```

## 5. Parameters Selections
*   **Iteration Count**: Typically 100–1000 iterations for the Gauss-Seidel solver, or use a direct sparse solver for large meshes.
*   **Boundary Mapping**: Usually based on normalized arc-length to prevent the boundary vertices from "bunching up" in corners.

## 6. Complexity
*   **Time Complexity**: $O(n \cdot i)$ for the iterative solver (where $n$ is vertices, $i$ is iterations). $O(n \log n)$ or $O(n^{1.5})$ for direct sparse solvers.
*   **Space Complexity**: $O(n + e)$ to store the mesh connectivity and vertex positions.

## 7. Usages
*   **Shape Morphing**: Smoothly transitioning one 3D model into another with the same topology.
*   **Texture Mapping**: Unwrapping a 3D surface onto a 2D plane (UV mapping).
*   **Remeshing**: Transferring a high-quality triangulation onto a newly defined boundary.
*   **Surface Reconstruction**: Mapping a template mesh onto scanned point cloud data.

## 8. Testing methods and Edge cases
*   **Non-Convex Boundaries**: Tutte's theorem only guarantees no edge crossings for convex boundaries. For non-convex boundaries, self-intersections (flipped triangles) may occur.
*   **Disconnected Components**: The algorithm must be applied to each connected component of the mesh separately.
*   **High Valence Vertices**: Vertices with many neighbors may converge more slowly.
*   **Meshes with Holes**: Requires mapping multiple boundary cycles (e.g., one to the outer boundary, others to internal "islands").

## 9. References
*   Tutte, W. T. (1963). "How to draw a graph". Proceedings of the London Mathematical Society.
*   Floater, M. S. (1997). "Parametrization and smooth approximation of surface triangulations". Computer Aided Geometric Design.
*   Pinkall, U., & Polthier, K. (1993). "Computing discrete minimal surfaces and their conjugates". Computing.
*   [Wikipedia: Tutte embedding](https://en.wikipedia.org/wiki/Tutte_embedding)
