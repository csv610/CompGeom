# Incremental Delaunay Triangulation

## 1. Overview
Incremental Delaunay triangulation is a fundamental algorithm for constructing a Delaunay triangulation of a set of points in the plane. The algorithm builds the triangulation by adding points one at a time and locally updating the mesh to maintain the Delaunay property. It is valued for its relative simplicity and efficiency, especially when combined with spatial sorting techniques.

## 2. Definitions
*   **Delaunay Property**: A triangulation is Delaunay if the circumcircle of every triangle in the mesh contains no other points from the input set.
*   **In-Circle Test**: A geometric predicate that determines if a point $D$ lies inside, on, or outside the circumcircle of triangle $ABC$.
*   **Edge Flip**: Replacing the common edge of two adjacent triangles with an edge connecting their opposite vertices.
*   **Legal Edge**: An edge is "legal" if the circumcircle of one of its adjacent triangles does not contain the vertex of the other triangle.

## 3. Theory
The algorithm relies on the fact that any triangulation can be converted into a Delaunay triangulation through a series of edge flips. When a new point $P$ is inserted into a triangle $T$, it is connected to the three vertices of $T$, creating three new triangles. The edges of these new triangles (which were the edges of $T$) may now be "illegal." The algorithm recursively checks and flips these edges until the Delaunay property is restored globally.

## 4. Pseudo code
```python
function IncrementalDelaunay(points):
    # 1. Initialize with a super-triangle
    ST = CreateSuperTriangle(points)
    Triangulation = {ST}
    
    # 2. Add points one by one
    for p in points:
        T = FindTriangleContaining(p, Triangulation)
        SplitTriangle(T, p, Triangulation)
        
    # 3. Final cleanup
    RemoveSuperTriangleVertices(Triangulation)
    return Triangulation

function SplitTriangle(T, p, Triangulation):
    (A, B, C) = T.vertices
    NewTris = [(p, A, B), (p, B, C), (p, C, A)]
    Replace T with NewTris in Triangulation
    for each edge in {AB, BC, CA}:
        LegalizeEdge(p, edge, Triangulation)

function LegalizeEdge(p, edge(U, V), Triangulation):
    Neighbor = FindNeighbor(edge, Triangulation)
    if Neighbor is None: return
    
    W = Neighbor.vertex_opposite_to(edge)
    if InCircle(p, U, V, W):
        FlipEdge(edge(U, V)) to edge(p, W)
        LegalizeEdge(p, edge(U, W), Triangulation)
        LegalizeEdge(p, edge(W, V), Triangulation)
```

## 5. Parameters Selections
*   **Point Location**: Using a **Visibility Walk** or a **Point Grid** (spatial index) drastically speeds up finding the triangle containing the new point.
*   **Insertion Order**: Sorting points along a **Hilbert Curve** or **Morton Code** ensures that subsequent points are geographically close, keeping the walk short.

## 6. Complexity
*   **Time Complexity**: Average case $O(n \log n)$ with spatial sorting and efficient point location. Worst case $O(n^2)$ for highly structured point sets without randomization or sorting.
*   **Space Complexity**: $O(n)$ to store the triangles and point coordinates.

## 7. Usages
*   Generating high-quality meshes for Finite Element Method (FEM) analysis.
*   Interpolation of scattered data (e.g., creating contour maps from elevation points).
*   Pathfinding in robotics and video games.
*   Dual representation of Voronoi diagrams.

## 8. Testing methods and Edge cases
*   **Co-circular Points**: Four or more points on the same circle. The algorithm will choose one valid triangulation, but the result may not be unique.
*   **Collinear Points**: Points lying on a single line. Requires robust predicates or a small perturbation (epsilon).
*   **Points on Edges**: If a point falls exactly on an existing edge, the edge should be split into four triangles instead of three.
*   **Super-Triangle Selection**: Must be large enough to contain all points, but not so large that it causes numerical overflow.

## 9. References
*   Bowyer, A. (1981). "Computing Dirichlet tessellations". The Computer Journal.
*   Watson, D. F. (1981). "Computing the n-dimensional Delaunay tessellation with application to Voronoi polytopes". The Computer Journal.
*   Guibas, L., & Stolfi, J. (1985). "Primitives for the manipulation of general subdivisions and the computation of Voronoi diagrams". ACM Transactions on Graphics.
*   [Wikipedia: Delaunay triangulation](https://en.wikipedia.org/wiki/Delaunay_triangulation)
