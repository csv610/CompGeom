# Hodge Star Computation (Discrete Exterior Calculus)

## 1. Overview
The Hodge star operator ($*$) is a fundamental tool in Riemannian geometry and exterior calculus that establishes a correspondence between $k$-forms and $(n-k)$-forms. In Discrete Exterior Calculus (DEC), the Hodge star operator is represented as a diagonal matrix that maps discrete forms on a primal mesh to discrete forms on its dual mesh. It is essential for solving partial differential equations (PDEs), such as the Poisson equation or Maxwell's equations, on triangle meshes.

## 2. Definitions
*   **Discrete k-form**: A scalar value associated with each $k$-simplex of a mesh (0-form: vertex, 1-form: edge, 2-form: face).
*   **Primal Mesh**: The original triangular mesh.
*   **Dual Mesh**: Typically the Voronoi diagram or the circumcentric dual of the primal mesh.
*   **Hodge Star ($\star$)**: An operator that maps a discrete form on a primal simplex to its dual simplex, preserving "flow" or "intensity" across the two.

## 3. Theory
In 2D (surface meshes), the discrete Hodge star operators are typically defined as follows:
*   **0-star ($\star_0$)**: Maps a value at a primal vertex to its dual Voronoi cell. $\star_0 = \frac{\text{Area(Dual Cell)}}{\text{Area(Primal Vertex)}} = \text{Area(Dual Cell)}$.
*   **1-star ($\star_1$)**: Maps a value on a primal edge to its dual Voronoi edge. $\star_1 = \frac{\text{Length(Dual Edge)}}{\text{Length(Primal Edge)}}$. This is the famous **cotangent weight** ratio: $\frac{1}{2}(\cot \alpha + \cot \beta)$.
*   **2-star ($\star_2$)**: Maps a value on a primal face to its dual Voronoi vertex. $\star_2 = \frac{\text{Area(Dual Vertex)}}{\text{Area(Primal Face)}} = \frac{1}{\text{Area(Primal Face)}}$.

These operators allow for the definition of the **Discrete Laplace-Beltrami Operator** as $\Delta = \star_0^{-1} d^\top \star_1 d$, where $d$ is the discrete exterior derivative.

## 4. Pseudo code
```python
function ComputeHodgeStars(mesh):
    # 1. 0-Star (Vertex areas)
    star0 = DiagonalMatrix(n_vertices)
    for v in mesh.vertices:
        star0[v, v] = ComputeVoronoiArea(v, mesh)
        
    # 2. 1-Star (Edge cotangent weights)
    star1 = DiagonalMatrix(n_edges)
    for edge in mesh.edges:
        # Get angles alpha, beta opposite to the edge in its two incident faces
        alpha, beta = GetOppositeAngles(edge, mesh)
        star1[edge, edge] = 0.5 * (cot(alpha) + cot(beta))
        
    # 3. 2-Star (Face areas)
    star2 = DiagonalMatrix(n_faces)
    for face in mesh.faces:
        star2[face, face] = 1.0 / ComputeFaceArea(face, mesh)
        
    return star0, star1, star2
```

## 5. Parameters Selections
*   **Dual Mesh Choice**: The **Circumcentric Dual** is preferred because primal edges are perpendicular to dual edges, simplifying the star operator to a simple ratio.
*   **Robustness**: Cotangent weights can become negative if the mesh contains obtuse triangles. Using an intrinsic Delaunay triangulation or an epsilon-clamping can mitigate this.

## 6. Complexity
*   **Time Complexity**: $O(F)$, where $F$ is the number of faces, to calculate all local geometric properties (areas, lengths, angles).
*   **Space Complexity**: $O(V + E + F)$ to store the diagonal matrices.

## 7. Usages
*   **Surface Parameterization**: Constructing the Laplacian matrix for Harmonic Mapping or LSCM.
*   **Mesh Smoothing**: Implementing Mean Curvature Flow using the DEC Laplacian.
*   **Fluid Simulation on Surfaces**: Solving the Navier-Stokes equations using discrete forms.
*   **Geodesic Distances**: Implementing the Heat Method for distance calculation.
*   **Texture Synthesis**: Generating procedural textures by solving reaction-diffusion equations on meshes.

## 8. Testing methods and Edge cases
*   **Flat Plane**: On a regular grid, the cotangent weights should simplify to the standard 5-point Laplacian stencil.
*   **Equilateral Triangles**: All cotangent weights should be exactly $\cot(60^\circ) = 1/\sqrt{3}$.
*   **Obtuse Triangles**: Verify that negative cotangent weights are handled or expected (they can cause instability in some solvers).
*   **Boundaries**: Vertices and edges on the boundary have only one incident face; their Hodge star contributions must be halved or handled carefully.

## 9. References
*   Desbrun, M., Hirani, A. N., Leok, M., & Marsden, J. E. (2005). "Discrete Exterior Calculus". arXiv preprint.
*   Crane, K., Weischedel, C., & Wardetzky, M. (2013). "Digital Geometry Processing with Discrete Exterior Calculus". SIGGRAPH Course.
*   Pinkall, U., & Polthier, K. (1993). "Computing discrete minimal surfaces and their conjugates". Computing.
*   [Wikipedia: Discrete exterior calculus](https://en.wikipedia.org/wiki/Discrete_exterior_calculus)
