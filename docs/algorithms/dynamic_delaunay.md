# Dynamic Delaunay Triangulation

## 1. Overview
Dynamic Delaunay triangulation is the process of maintaining a Delaunay triangulation as points are inserted into or deleted from the set. Unlike static construction, where the entire point set is known beforehand, dynamic algorithms must update the mesh locally to restore the Delaunay property while maintaining efficiency. This is critical for applications involving moving objects, real-time data streams, and interactive geometry editing.

## 2. Definitions
*   **Insertion**: Adding a new point $P$ and updating the triangulation to include $P$.
*   **Deletion**: Removing an existing vertex $V$ and re-triangulating the "hole" left behind.
*   **Point Location**: The sub-problem of finding which triangle in the current mesh contains the new point $P$.
*   **Edge Flip**: The fundamental operation used to restore the Delaunay property after an insertion or deletion.

## 3. Theory
### Insertion
Insertion typically uses the **Incremental Algorithm**:
1.  **Locate**: Find triangle $T$ containing new point $P$.
2.  **Split**: Split $T$ into three new triangles by connecting $P$ to its vertices.
3.  **Legalize**: Recursively check the edges of the new triangles and perform **Delaunay Flips** until all edges are legal (satisfy the empty circumcircle property).

### Deletion
Deletion is more complex:
1.  **Remove**: Remove the vertex $V$ and all incident edges, leaving a star-shaped polygon (the "hole").
2.  **Re-triangulate**: Triangulate the hole. A simple way is to use a recursive "ear clipping" approach that specifically chooses diagonals satisfying the Delaunay property.
3.  **Legalize**: Alternatively, perform any triangulation of the hole and then flip edges until it is Delaunay.

## 4. Pseudo code
### Dynamic Insertion
```python
function InsertPoint(triangulation, p):
    # 1. Point Location
    T = FindTriangleContaining(triangulation, p)
    
    # 2. Local Update
    new_triangles = SplitTriangle(T, p)
    
    # 3. Restore Delaunay Property
    # Check edges of the new triangles against the InCircle test
    edges_to_check = GetOuterEdges(new_triangles)
    while edges_to_check:
        e = edges_to_check.pop()
        if IsIllegal(e, triangulation):
            new_e = Flip(e, triangulation)
            edges_to_check.extend(GetSurroundingEdges(new_e))
```

### Dynamic Deletion
```python
function DeletePoint(triangulation, v):
    # 1. Identify neighbors
    neighbors = GetAdjacentVertices(v, triangulation)
    
    # 2. Remove vertex and incident faces
    RemoveVertex(v, triangulation)
    
    # 3. Fill the resulting hole (Star-shaped polygon)
    # A common method is the "Recursive Delaunay Filling"
    FillHoleDelaunay(neighbors, triangulation)
```

## 5. Parameters Selections
*   **Point Location Strategy**: For high performance, use a **Stochastic Walk** or a **Directed Acyclic Graph (DAG)** (e.g., the Delaunay Tree) to achieve $O(\log n)$ location time.
*   **Robustness**: Use robust predicates to prevent infinite loops during flipping caused by precision errors.

## 6. Complexity
*   **Insertion**: $O(\log n)$ average for location, $O(1)$ expected for flipping (though $O(n)$ worst-case).
*   **Deletion**: $O(\log n)$ average to find the vertex, $O(k)$ to re-triangulate where $k$ is the degree of the vertex.
*   **Space**: $O(n)$ to store the triangles and point location structures.

## 7. Usages
*   **Terrain Modeling**: Adding new survey points to a digital elevation model.
*   **Robotics**: Updating a map as a robot moves and discovers new obstacles.
*   **Fluid Simulation**: Re-meshing around a moving boundary (e.g., a boat moving through water).
*   **Mesh Refinement**: Splitting triangles to improve resolution in high-gradient areas.
*   **Data Visualization**: Real-time plotting of scattered data points.

## 8. Testing methods and Edge cases
*   **Co-circular Points**: Ensure both insertion and deletion handle cases where four or more points lie on a circle (Delaunay triangulation is not unique).
*   **Points on Boundary**: Handle points added to or removed from the convex hull correctly.
*   **Degenerate Deletion**: Deleting a vertex that reduces the convex hull to a line or a single point.
*   **Multiple Insertions at same position**: Handle duplicate points by ignoring them or updating metadata.
*   **High-Valence Vertices**: Test deletion of vertices shared by many (e.g., 50+) triangles.

## 9. References
*   Bowyer, A. (1981). "Computing Dirichlet tessellations". The Computer Journal.
*   Watson, D. F. (1981). "Computing the n-dimensional Delaunay tessellation with application to Voronoi polytopes". The Computer Journal.
*   Guibas, L., Knuth, D. E., & Sharir, M. (1992). "Randomized incremental construction of Delaunay and Voronoi diagrams". Algorithmica.
*   Devillers, O. (1999). "On handling transitions between different structures in geometric modeling". Proceedings of the 11th Canadian Conference on Computational Geometry.
*   Wikipedia: [Delaunay triangulation](https://en.wikipedia.org/wiki/Delaunay_triangulation)
