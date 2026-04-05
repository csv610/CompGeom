# Discrete Exterior Derivative

## 1. Overview
The exterior derivative ($d$) is a fundamental operator in differential geometry that generalizes the concepts of gradient, curl, and divergence to higher-dimensional forms. In Discrete Exterior Calculus (DEC), the exterior derivative is a sparse matrix that acts as a topological operator, mapping discrete $k$-forms on a mesh to discrete $(k+1)$-forms. It depends purely on the connectivity of the mesh (its boundary relationships) and is independent of the mesh's geometric coordinates.

## 2. Definitions
*   **Discrete k-form ($\omega^k$)**: A vector of scalar values, where each entry is associated with a $k$-simplex of the mesh (0-simplex: vertex, 1-simplex: edge, 2-simplex: face).
*   **Chain Complex**: A sequence of vector spaces of $k$-chains connected by boundary operators ($\partial$).
*   **Cochain Complex**: A sequence of vector spaces of $k$-forms connected by exterior derivatives ($d$).
*   **Boundary Relationship ($\partial$)**: The boundary of a 1-simplex (edge) is its two 0-simplices (vertices). The boundary of a 2-simplex (triangle) is its three 1-simplices (edges).

## 3. Theory
The discrete exterior derivative $d_k$ is the **dual of the boundary operator** $\partial_{k+1}$ from the primal mesh. Specifically, it maps a value on a $k$-simplex to its incident $(k+1)$-simplices based on orientation.
*   **0-derivative ($d_0$)**: Maps a value at vertices to its incident edges. $d_0(\phi)_{(u,v)} = \phi_v - \phi_u$. This is the discrete equivalent of the **Gradient**.
*   **1-derivative ($d_1$)**: Maps a value on edges to its incident faces. $d_1(\alpha)_{(u,v,w)} = \alpha_{uv} + \alpha_{vw} + \alpha_{wu}$ (where indices are oriented). This is the discrete equivalent of the **Curl**.

A critical property of the exterior derivative is that **$d \circ d = 0$**, meaning the derivative of a derivative is always zero. This is the discrete version of the identities $\nabla \times (\nabla \phi) = 0$ and $\nabla \cdot (\nabla \times A) = 0$.

## 4. Pseudo code
```python
function ComputeExteriorDerivatives(mesh):
    # 1. d0 (0-forms to 1-forms)
    d0 = SparseMatrix(n_edges, n_vertices)
    for edge in mesh.edges:
        u, v = edge.start_vertex, edge.end_vertex
        d0[edge_id, v] = 1
        d0[edge_id, u] = -1
        
    # 2. d1 (1-forms to 2-forms)
    d1 = SparseMatrix(n_faces, n_edges)
    for face in mesh.faces:
        for edge_id, orientation in GetOrientedEdges(face):
            # Orientation is 1 if edge matches face order, -1 otherwise
            d1[face_id, edge_id] = orientation
            
    return d0, d1
```

## 5. Parameters Selections
*   **Orientation**: All simplices must be consistently oriented. Primal edges are typically oriented by vertex ID (e.g., $u \to v$ if $u < v$). Primal faces are usually CCW.
*   **Sparse Representation**: Since each simplex has only a few neighbors, $d$ matrices are extremely sparse; CSR or CSC formats are essential for performance.

## 6. Complexity
*   **Time Complexity**: $O(F)$, where $F$ is the number of faces, as we iterate through each face and edge relationship once.
*   **Space Complexity**: $O(E + F)$ to store the sparse matrix entries.

## 7. Usages
*   **Vector Field Processing**: Decomposing vector fields into curl-free and divergence-free components (Hodge Decomposition).
*   **Surface Parameterization**: Representing gradients of scalar functions used in UV mapping.
*   **Fluid Simulation**: Enforcing divergence-free conditions on flow velocities.
*   **Solving PDEs**: Formulating the Poisson or Heat equation using the DEC Laplacian $\Delta = \star^{-1} d^\top \star d$.
*   **Topology Analysis**: Computing Betti numbers or identifying mesh "holes" using homology.

## 8. Testing methods and Edge cases
*   **d o d Property**: Verify that $d_1 \times d_0$ results in a matrix where all entries are near zero (floating point) or exactly zero (integer).
*   **Single Triangle**: On a single triangle, the sum of edge values around the boundary must match the face derivative.
*   **Disconnected Mesh**: The matrices should naturally decompose into block-diagonal structures for each component.
*   **Boundaries**: Ensure that orientation is handled correctly for edges on the mesh boundary.

## 9. References
*   Desbrun, M., Hirani, A. N., Leok, M., & Marsden, J. E. (2005). "Discrete Exterior Calculus". arXiv preprint.
*   Crane, K., Weischedel, C., & Wardetzky, M. (2013). "Digital Geometry Processing with Discrete Exterior Calculus". SIGGRAPH Course.
*   Wikipedia: [Exterior derivative](https://en.wikipedia.org/wiki/Exterior_derivative)
